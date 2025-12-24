"""Multi-modal extraction service for tables and images."""

import io
import os
import tempfile
from dataclasses import dataclass
from typing import Any

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from core.embeddings import get_embeddings
from core.models import ExtractedImage, ExtractedTable
from core.vector_store import get_vector_store


@dataclass
class TableInfo:
    """Information about an extracted table."""

    table_index: int
    page_number: int | None
    num_rows: int
    num_cols: int
    caption: str | None
    markdown_content: str
    html_content: str
    csv_content: str


@dataclass
class ImageInfo:
    """Information about an extracted image."""

    image_index: int
    page_number: int | None
    image_type: str
    width: int
    height: int
    file_path: str
    caption: str | None


def extract_tables_from_document(document: Any) -> list[TableInfo]:
    """Extract all tables from a Docling document."""
    tables = []

    if not hasattr(document, "tables") or not document.tables:
        return tables

    for idx, table in enumerate(document.tables):
        try:
            df: pd.DataFrame = table.export_to_dataframe(doc=document)
            markdown = df.to_markdown(index=False) if not df.empty else ""
            html = table.export_to_html(doc=document)

            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()

            page_number = None
            if hasattr(table, "prov") and table.prov:
                prov = table.prov[0] if table.prov else None
                if prov and hasattr(prov, "page_no"):
                    page_number = prov.page_no

            caption = None
            if hasattr(table, "captions") and table.captions:
                caption = table.captions[0].text if table.captions else None

            tables.append(TableInfo(
                table_index=idx,
                page_number=page_number,
                num_rows=len(df),
                num_cols=len(df.columns) if not df.empty else 0,
                caption=caption,
                markdown_content=markdown,
                html_content=html,
                csv_content=csv_content,
            ))
        except Exception:
            continue

    return tables


def extract_images_from_document(
    document: Any,
    output_dir: str | None = None,
) -> list[ImageInfo]:
    """Extract all images from a Docling document."""
    images = []

    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="docling_images_")

    os.makedirs(output_dir, exist_ok=True)

    if not hasattr(document, "pictures") or not document.pictures:
        if hasattr(document, "pages"):
            for page_idx, page in document.pages.items():
                if hasattr(page, "image") and page.image:
                    img = page.image
                    file_path = os.path.join(output_dir, f"page_{page_idx}.png")
                    img.save(file_path, format="PNG")

                    images.append(ImageInfo(
                        image_index=len(images),
                        page_number=page_idx,
                        image_type="page_render",
                        width=img.width,
                        height=img.height,
                        file_path=file_path,
                        caption=None,
                    ))
        return images

    for idx, picture in enumerate(document.pictures):
        try:
            page_number = None
            if hasattr(picture, "prov") and picture.prov:
                prov = picture.prov[0] if picture.prov else None
                if prov and hasattr(prov, "page_no"):
                    page_number = prov.page_no

            caption = None
            if hasattr(picture, "captions") and picture.captions:
                caption = picture.captions[0].text if picture.captions else None

            img = None
            if hasattr(picture, "image") and picture.image:
                img = picture.image
            elif hasattr(picture, "get_image"):
                img = picture.get_image(document)

            if img:
                file_path = os.path.join(output_dir, f"image_{idx}.png")
                img.save(file_path, format="PNG")

                images.append(ImageInfo(
                    image_index=idx,
                    page_number=page_number,
                    image_type="embedded",
                    width=img.width,
                    height=img.height,
                    file_path=file_path,
                    caption=caption,
                ))
        except Exception:
            continue

    return images


async def process_tables(
    db: AsyncSession,
    document_id: int,
    document: Any,
    generate_embeddings: bool = True,
) -> list[ExtractedTable]:
    """Extract tables from document and store them."""
    table_infos = extract_tables_from_document(document)

    if not table_infos:
        return []

    tables = []
    for info in table_infos:
        table = ExtractedTable(
            document_id=document_id,
            table_index=info.table_index,
            page_number=info.page_number,
            num_rows=info.num_rows,
            num_cols=info.num_cols,
            caption=info.caption,
            markdown_content=info.markdown_content,
            html_content=info.html_content,
            csv_content=info.csv_content,
            has_embedding=False,
        )
        tables.append(table)

    db.add_all(tables)
    await db.commit()

    for table in tables:
        await db.refresh(table)

    if generate_embeddings and tables:
        embeddings_service = get_embeddings()
        vector_store = get_vector_store(embeddings_service.dimension)

        texts = []
        for t in tables:
            text = f"Table: {t.caption or 'Untitled'}\n{t.markdown_content}"
            texts.append(text)

        embeddings = embeddings_service.embed(texts)

        for table, emb in zip(tables, embeddings):
            vector_store.add(table.id + 1000000, emb)
            table.has_embedding = True

        await db.commit()

    return tables


async def process_images(
    db: AsyncSession,
    document_id: int,
    document: Any,
    output_dir: str | None = None,
) -> list[ExtractedImage]:
    """Extract images from document and store them."""
    image_infos = extract_images_from_document(document, output_dir)

    if not image_infos:
        return []

    images = []
    for info in image_infos:
        image = ExtractedImage(
            document_id=document_id,
            image_index=info.image_index,
            page_number=info.page_number,
            image_type=info.image_type,
            width=info.width,
            height=info.height,
            file_path=info.file_path,
            caption=info.caption,
            has_embedding=False,
        )
        images.append(image)

    db.add_all(images)
    await db.commit()

    for image in images:
        await db.refresh(image)

    return images


async def generate_table_summary(
    table: ExtractedTable,
    llm_provider: str = "openai",
    api_key: str | None = None,
) -> str:
    """Generate a natural language summary of a table using LLM."""
    from core.llm import get_llm_provider

    llm = get_llm_provider(llm_provider, api_key=api_key)

    prompt = f"""Summarize this table in 2-3 sentences. Focus on the key data points and what the table represents.

Table:
{table.markdown_content}"""

    summary = await llm.generate(prompt, context=[])
    return summary


async def query_table_with_llm(
    table: ExtractedTable,
    query: str,
    llm_provider: str = "openai",
    api_key: str | None = None,
) -> str:
    """Answer a question about a specific table using LLM."""
    from core.llm import get_llm_provider

    llm = get_llm_provider(llm_provider, api_key=api_key)

    prompt = f"""Based on the following table data, answer the question.

Table:
{table.markdown_content}

Question: {query}"""

    answer = await llm.generate(prompt, context=[])
    return answer
