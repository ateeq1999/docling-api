"""Semantic search endpoints."""

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    RAGRequest,
    RAGResponseSchema,
    SourceInfo,
)
from services.rag_service import RAGService

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Semantic search across all documents."""
    rag = RAGService(db)
    results = await rag.search(
        query=request.query,
        top_k=request.top_k,
        document_ids=request.document_ids,
        file_types=request.file_types,
    )

    return SearchResponse(
        query=request.query,
        results=[
            SearchResultItem(
                chunk_id=r.chunk_id,
                document_id=r.document_id,
                filename=r.filename,
                content=r.content,
                score=r.score,
                page_number=r.page_number,
                section_title=r.section_title,
            )
            for r in results
        ],
    )


@router.post("/ask", response_model=RAGResponseSchema)
async def ask(
    request: RAGRequest,
    db: AsyncSession = Depends(get_db),
    x_openai_api_key: str | None = Header(None, alias="X-OpenAI-API-Key"),
):
    """Ask a question using RAG (Retrieval-Augmented Generation)."""
    rag = RAGService(db)
    response = await rag.answer(
        query=request.query,
        top_k=request.top_k,
        document_ids=request.document_ids,
        llm_provider=request.llm_provider,
        llm_model=request.llm_model,
        api_key=x_openai_api_key,
    )

    return RAGResponseSchema(
        answer=response.answer,
        sources=[
            SourceInfo(
                chunk_id=s.chunk_id,
                document_id=s.document_id,
                filename=s.filename,
                content=s.content,
                score=s.score,
                page_number=s.page_number,
            )
            for s in response.sources
        ],
    )
