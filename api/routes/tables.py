"""Table extraction and querying endpoints."""

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Document, ExtractedTable

router = APIRouter(
    prefix="/tables",
    tags=["tables"],
)


class TableResponse(BaseModel):
    id: int
    document_id: int
    table_index: int
    page_number: int | None
    num_rows: int
    num_cols: int
    caption: str | None
    markdown_content: str
    summary: str | None
    has_embedding: bool
    created_at: str | None


class TableQueryRequest(BaseModel):
    query: str
    llm_provider: str = "openai"


class TableQueryResponse(BaseModel):
    table_id: int
    query: str
    answer: str


class TableSummaryResponse(BaseModel):
    table_id: int
    summary: str


@router.get("/document/{document_id}", response_model=list[TableResponse])
async def get_document_tables(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all tables extracted from a document."""
    doc_result = await db.execute(select(Document).where(Document.id == document_id))
    if not doc_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")

    result = await db.execute(
        select(ExtractedTable)
        .where(ExtractedTable.document_id == document_id)
        .order_by(ExtractedTable.table_index)
    )
    tables = result.scalars().all()

    return [
        TableResponse(
            id=t.id,
            document_id=t.document_id,
            table_index=t.table_index,
            page_number=t.page_number,
            num_rows=t.num_rows,
            num_cols=t.num_cols,
            caption=t.caption,
            markdown_content=t.markdown_content,
            summary=t.summary,
            has_embedding=bool(t.has_embedding),
            created_at=t.created_at.isoformat() if t.created_at else None,
        )
        for t in tables
    ]


@router.get("/{table_id}", response_model=TableResponse)
async def get_table(
    table_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single table by ID."""
    result = await db.execute(
        select(ExtractedTable).where(ExtractedTable.id == table_id)
    )
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    return TableResponse(
        id=table.id,
        document_id=table.document_id,
        table_index=table.table_index,
        page_number=table.page_number,
        num_rows=table.num_rows,
        num_cols=table.num_cols,
        caption=table.caption,
        markdown_content=table.markdown_content,
        summary=table.summary,
        has_embedding=bool(table.has_embedding),
        created_at=table.created_at.isoformat() if table.created_at else None,
    )


@router.get("/{table_id}/html")
async def get_table_html(
    table_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get table as HTML."""
    result = await db.execute(
        select(ExtractedTable).where(ExtractedTable.id == table_id)
    )
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    return Response(content=table.html_content or "", media_type="text/html")


@router.get("/{table_id}/csv")
async def get_table_csv(
    table_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get table as CSV."""
    result = await db.execute(
        select(ExtractedTable).where(ExtractedTable.id == table_id)
    )
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    return Response(content=table.csv_content or "", media_type="text/csv")


@router.post("/{table_id}/query", response_model=TableQueryResponse)
async def query_table(
    table_id: int,
    request: TableQueryRequest,
    db: AsyncSession = Depends(get_db),
    x_openai_api_key: str | None = Header(None, alias="X-OpenAI-API-Key"),
):
    """Query a table using natural language."""
    from services.multimodal_service import query_table_with_llm

    result = await db.execute(
        select(ExtractedTable).where(ExtractedTable.id == table_id)
    )
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    answer = await query_table_with_llm(
        table=table,
        query=request.query,
        llm_provider=request.llm_provider,
        api_key=x_openai_api_key,
    )

    return TableQueryResponse(
        table_id=table_id,
        query=request.query,
        answer=answer,
    )


@router.post("/{table_id}/summarize", response_model=TableSummaryResponse)
async def summarize_table(
    table_id: int,
    db: AsyncSession = Depends(get_db),
    x_openai_api_key: str | None = Header(None, alias="X-OpenAI-API-Key"),
):
    """Generate a summary of a table."""
    from services.multimodal_service import generate_table_summary

    result = await db.execute(
        select(ExtractedTable).where(ExtractedTable.id == table_id)
    )
    table = result.scalar_one_or_none()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    summary = await generate_table_summary(
        table=table,
        api_key=x_openai_api_key,
    )

    table.summary = summary
    await db.commit()

    return TableSummaryResponse(
        table_id=table_id,
        summary=summary,
    )
