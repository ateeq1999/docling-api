"""Chunk management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Chunk, Document
from core.schemas import ChunkResponse, ChunksResponse

router = APIRouter(
    prefix="/chunks",
    tags=["chunks"],
)


@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single chunk by ID."""
    result = await db.execute(select(Chunk).where(Chunk.id == chunk_id))
    chunk = result.scalar_one_or_none()

    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")

    return ChunkResponse(
        id=chunk.id,
        document_id=chunk.document_id,
        content=chunk.content,
        context=chunk.context,
        chunk_index=chunk.chunk_index,
        page_number=chunk.page_number,
        section_title=chunk.section_title,
        token_count=chunk.token_count,
        metadata=chunk.get_metadata(),
        has_embedding=bool(chunk.has_embedding),
        created_at=chunk.created_at,
    )


@router.get("/document/{document_id}", response_model=ChunksResponse)
async def get_document_chunks(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all chunks for a document."""
    doc_result = await db.execute(select(Document).where(Document.id == document_id))
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = await db.execute(
        select(Chunk)
        .where(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index)
    )
    chunks = result.scalars().all()

    return ChunksResponse(
        count=len(chunks),
        chunks=[
            ChunkResponse(
                id=c.id,
                document_id=c.document_id,
                content=c.content,
                context=c.context,
                chunk_index=c.chunk_index,
                page_number=c.page_number,
                section_title=c.section_title,
                token_count=c.token_count,
                metadata=c.get_metadata(),
                has_embedding=bool(c.has_embedding),
                created_at=c.created_at,
            )
            for c in chunks
        ],
    )
