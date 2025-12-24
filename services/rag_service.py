"""RAG (Retrieval-Augmented Generation) service."""

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.embeddings import get_embeddings, SentenceTransformerEmbeddings
from core.llm import LLMProvider, get_llm_provider
from core.models import Chunk, Document
from core.vector_store import get_vector_store, SQLiteVectorStore


@dataclass
class SearchResult:
    """A single search result."""

    chunk_id: int
    document_id: int
    filename: str
    content: str
    context: str
    score: float
    page_number: int | None
    section_title: str | None


@dataclass
class RAGResponse:
    """Response from RAG query."""

    answer: str
    sources: list[SearchResult]


class RAGService:
    """Service for RAG operations."""

    def __init__(
        self,
        db: AsyncSession,
        embeddings: SentenceTransformerEmbeddings | None = None,
        vector_store: SQLiteVectorStore | None = None,
        llm: LLMProvider | None = None,
    ):
        self.db = db
        self.embeddings = embeddings or get_embeddings()
        self.vector_store = vector_store or get_vector_store(self.embeddings.dimension)
        self.llm = llm

    async def search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: list[int] | None = None,
        file_types: list[str] | None = None,
    ) -> list[SearchResult]:
        """Search for relevant chunks."""
        query_embedding = await self.embeddings.embed_query_async(query)
        
        search_top_k = top_k * 3 if document_ids or file_types else top_k
        vector_results = self.vector_store.search(query_embedding, top_k=search_top_k)

        if not vector_results:
            return []

        chunk_ids = [r[0] for r in vector_results]
        distances = {r[0]: r[1] for r in vector_results}

        stmt = (
            select(Chunk, Document)
            .join(Document, Chunk.document_id == Document.id)
            .where(Chunk.id.in_(chunk_ids))
        )

        if document_ids:
            stmt = stmt.where(Chunk.document_id.in_(document_ids))
        if file_types:
            stmt = stmt.where(Document.file_type.in_(file_types))

        result = await self.db.execute(stmt)
        rows = result.all()

        results = []
        for chunk, doc in rows:
            distance = distances.get(chunk.id, 0.0)
            score = 1.0 / (1.0 + distance)

            results.append(SearchResult(
                chunk_id=chunk.id,
                document_id=doc.id,
                filename=doc.filename,
                content=chunk.content,
                context=chunk.context,
                score=score,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    async def answer(
        self,
        query: str,
        top_k: int = 5,
        document_ids: list[int] | None = None,
        llm_provider: str = "openai",
        llm_model: str | None = None,
        api_key: str | None = None,
    ) -> RAGResponse:
        """Answer a question using RAG."""
        sources = await self.search(
            query=query,
            top_k=top_k,
            document_ids=document_ids,
        )

        if not sources:
            return RAGResponse(
                answer="I couldn't find any relevant information to answer your question.",
                sources=[],
            )

        llm = self.llm or get_llm_provider(llm_provider, llm_model, api_key)
        contexts = [
            f"[Source: {s.filename}, Page: {s.page_number or 'N/A'}]\n{s.context}"
            for s in sources
        ]

        answer = await llm.generate(query, contexts)

        return RAGResponse(answer=answer, sources=sources)

    async def answer_stream(
        self,
        query: str,
        top_k: int = 5,
        document_ids: list[int] | None = None,
        llm_provider: str = "openai",
        llm_model: str | None = None,
        api_key: str | None = None,
    ) -> tuple[AsyncIterator[str], list[SearchResult]]:
        """Stream answer using RAG."""
        sources = await self.search(
            query=query,
            top_k=top_k,
            document_ids=document_ids,
        )

        if not sources:
            async def empty_stream():
                yield "I couldn't find any relevant information to answer your question."

            return empty_stream(), []

        llm = self.llm or get_llm_provider(llm_provider, llm_model, api_key)
        contexts = [
            f"[Source: {s.filename}, Page: {s.page_number or 'N/A'}]\n{s.context}"
            for s in sources
        ]

        return llm.stream(query, contexts), sources


async def process_and_embed_document(
    db: AsyncSession,
    document_id: int,
    document: any,
    embeddings: SentenceTransformerEmbeddings | None = None,
    vector_store: SQLiteVectorStore | None = None,
) -> int:
    """Process a document: chunk it and generate embeddings."""
    from services.chunking_service import chunk_document

    embeddings = embeddings or get_embeddings()
    vector_store = vector_store or get_vector_store(embeddings.dimension)

    chunk_results = await asyncio.to_thread(chunk_document, document)

    chunks = []
    for cr in chunk_results:
        chunk = Chunk(
            document_id=document_id,
            content=cr.text,
            context=cr.context,
            chunk_index=cr.chunk_index,
            page_number=cr.page_number,
            section_title=cr.section_title,
            token_count=cr.token_count,
            metadata_json=None,
            has_embedding=False,
        )
        chunk.set_metadata(cr.metadata)
        chunks.append(chunk)

    db.add_all(chunks)
    await db.commit()

    for chunk in chunks:
        await db.refresh(chunk)

    texts = [c.context for c in chunks]
    batch_embeddings = await embeddings.embed_async(texts)

    chunk_ids = [c.id for c in chunks]
    vector_store.add_batch(chunk_ids, batch_embeddings)

    for chunk in chunks:
        chunk.has_embedding = True
    await db.commit()

    return len(chunks)
