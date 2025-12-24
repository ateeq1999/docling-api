"""Advanced RAG techniques: HyDE, multi-query, re-ranking."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from core.embeddings import get_embeddings
from core.llm import get_llm_provider
from services.rag_service import RAGService, SearchResult


@dataclass
class RankedResult:
    """Search result with re-ranking score."""

    result: SearchResult
    original_score: float
    rerank_score: float
    final_score: float


async def generate_hypothetical_document(
    query: str,
    llm_provider: str = "openai",
    api_key: str | None = None,
) -> str:
    """
    HyDE: Generate a hypothetical document that would answer the query.
    This is then used for embedding-based search instead of the raw query.
    """
    llm = get_llm_provider(llm_provider, api_key=api_key)

    prompt = f"""Write a short paragraph that would be a perfect answer to this question.
Write as if you are quoting from a document that contains the answer.
Do not include phrases like "According to" or "The document says".
Just write the content directly.

Question: {query}

Answer paragraph:"""

    hypothetical_doc = await llm.generate(prompt, context=[])
    return hypothetical_doc


async def expand_query(
    query: str,
    num_variations: int = 3,
    llm_provider: str = "openai",
    api_key: str | None = None,
) -> list[str]:
    """
    Generate multiple query variations for multi-query retrieval.
    """
    llm = get_llm_provider(llm_provider, api_key=api_key)

    prompt = f"""Generate {num_variations} different ways to ask the following question.
Each variation should capture a different aspect or use different keywords.
Return only the questions, one per line.

Original question: {query}

Variations:"""

    response = await llm.generate(prompt, context=[])
    variations = [q.strip() for q in response.strip().split("\n") if q.strip()]
    return [query] + variations[:num_variations]


async def rewrite_query(
    query: str,
    llm_provider: str = "openai",
    api_key: str | None = None,
) -> str:
    """
    Rewrite query for better retrieval using LLM.
    """
    llm = get_llm_provider(llm_provider, api_key=api_key)

    prompt = f"""Rewrite the following question to be more specific and detailed for document search.
Add relevant keywords and technical terms that might appear in documents.
Return only the rewritten question.

Original: {query}

Rewritten:"""

    rewritten = await llm.generate(prompt, context=[])
    return rewritten.strip()


def compute_rerank_score(query: str, content: str) -> float:
    """
    Simple lexical re-ranking based on term overlap.
    For production, use a cross-encoder model.
    """
    query_terms = set(query.lower().split())
    content_terms = set(content.lower().split())

    if not query_terms:
        return 0.0

    overlap = len(query_terms & content_terms)
    return overlap / len(query_terms)


def rerank_results(
    query: str,
    results: list[SearchResult],
    alpha: float = 0.7,
) -> list[RankedResult]:
    """
    Re-rank search results using lexical overlap.
    
    Args:
        query: The search query
        results: Original search results
        alpha: Weight for original score (1-alpha for rerank score)
    """
    ranked = []
    for result in results:
        rerank_score = compute_rerank_score(query, result.content)
        final_score = alpha * result.score + (1 - alpha) * rerank_score

        ranked.append(RankedResult(
            result=result,
            original_score=result.score,
            rerank_score=rerank_score,
            final_score=final_score,
        ))

    ranked.sort(key=lambda x: x.final_score, reverse=True)
    return ranked


async def hyde_search(
    db: AsyncSession,
    query: str,
    top_k: int = 5,
    document_ids: list[int] | None = None,
    llm_provider: str = "openai",
    api_key: str | None = None,
) -> list[SearchResult]:
    """
    HyDE search: Generate hypothetical document and search with its embedding.
    """
    hypothetical_doc = await generate_hypothetical_document(
        query, llm_provider, api_key
    )

    embeddings = get_embeddings()
    hyde_embedding = await embeddings.embed_query_async(hypothetical_doc)

    from core.vector_store import get_vector_store
    from core.models import Chunk, Document
    from sqlalchemy import select

    vector_store = get_vector_store(embeddings.dimension)
    vector_results = vector_store.search(hyde_embedding, top_k=top_k * 2)

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

    result = await db.execute(stmt)
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


async def multi_query_search(
    db: AsyncSession,
    query: str,
    top_k: int = 5,
    num_queries: int = 3,
    document_ids: list[int] | None = None,
    llm_provider: str = "openai",
    api_key: str | None = None,
) -> list[SearchResult]:
    """
    Multi-query search: Generate query variations and merge results.
    Uses Reciprocal Rank Fusion (RRF) to combine results.
    """
    queries = await expand_query(query, num_queries, llm_provider, api_key)

    rag = RAGService(db)

    all_results: list[list[SearchResult]] = []
    for q in queries:
        results = await rag.search(q, top_k=top_k, document_ids=document_ids)
        all_results.append(results)

    chunk_scores: dict[int, float] = {}
    chunk_data: dict[int, SearchResult] = {}
    k = 60

    for results in all_results:
        for rank, result in enumerate(results):
            rrf_score = 1.0 / (k + rank + 1)
            chunk_scores[result.chunk_id] = chunk_scores.get(result.chunk_id, 0) + rrf_score
            chunk_data[result.chunk_id] = result

    sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)

    final_results = []
    for chunk_id, score in sorted_chunks[:top_k]:
        result = chunk_data[chunk_id]
        final_results.append(SearchResult(
            chunk_id=result.chunk_id,
            document_id=result.document_id,
            filename=result.filename,
            content=result.content,
            context=result.context,
            score=score,
            page_number=result.page_number,
            section_title=result.section_title,
        ))

    return final_results
