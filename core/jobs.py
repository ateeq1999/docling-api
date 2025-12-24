"""Background job definitions for ARQ."""

import logging

from sqlalchemy import select

from core.database import async_session
from core.embeddings import get_embeddings
from core.models import Chunk
from core.vector_store import get_vector_store

logger = logging.getLogger("docling_jobs")


async def process_document_embeddings(
    ctx: dict,
    document_id: int,
) -> dict:
    """Background job to generate embeddings for a document's chunks."""
    async with async_session() as db:
        result = await db.execute(
            select(Chunk)
            .where(Chunk.document_id == document_id, Chunk.has_embedding.is_(False))
        )
        chunks = list(result.scalars().all())

        if not chunks:
            return {"document_id": document_id, "processed": 0}

        embeddings_service = get_embeddings()
        vector_store = get_vector_store(embeddings_service.dimension)

        texts = [c.context for c in chunks]
        embeddings = await embeddings_service.embed_async(texts)

        chunk_ids = [c.id for c in chunks]
        vector_store.add_batch(chunk_ids, embeddings)

        for chunk in chunks:
            chunk.has_embedding = True

        await db.commit()

        return {"document_id": document_id, "processed": len(chunks)}


async def batch_embed_documents(
    ctx: dict,
    document_ids: list[int],
) -> dict:
    """Background job to embed multiple documents."""
    results = []
    for doc_id in document_ids:
        result = await process_document_embeddings(ctx, doc_id)
        results.append(result)
    return {"documents": results, "total": len(results)}


async def cleanup_orphan_embeddings(ctx: dict) -> dict:
    """Background job to clean up embeddings for deleted chunks."""
    async with async_session() as db:
        result = await db.execute(select(Chunk.id))
        valid_chunk_ids = set(row[0] for row in result.all())

    deleted = 0

    return {"deleted": deleted, "valid_chunks": len(valid_chunk_ids)}


async def generate_table_summaries(
    ctx: dict,
    document_id: int,
) -> dict:
    """Background job to generate summaries for all tables in a document."""
    from core.models import ExtractedTable
    from services.multimodal_service import generate_table_summary

    async with async_session() as db:
        result = await db.execute(
            select(ExtractedTable)
            .where(
                ExtractedTable.document_id == document_id,
                ExtractedTable.summary.is_(None),
            )
        )
        tables = list(result.scalars().all())

        summaries_generated = 0
        for table in tables:
            try:
                summary = await generate_table_summary(table)
                table.summary = summary
                summaries_generated += 1
            except Exception as e:
                logger.error(f"Failed to generate summary for table {table.id}: {e}")

        await db.commit()

        return {
            "document_id": document_id,
            "tables_found": len(tables),
            "summaries_generated": summaries_generated,
        }


class WorkerSettings:
    """ARQ worker settings."""

    functions = [
        process_document_embeddings,
        batch_embed_documents,
        cleanup_orphan_embeddings,
        generate_table_summaries,
    ]

    redis_settings = None

    job_timeout = 600
    max_jobs = 10
    poll_delay = 0.5

    @staticmethod
    async def on_startup(ctx: dict) -> None:
        """Called when worker starts."""
        logger.info("Background worker started")

    @staticmethod
    async def on_shutdown(ctx: dict) -> None:
        """Called when worker shuts down."""
        logger.info("Background worker shutting down")
