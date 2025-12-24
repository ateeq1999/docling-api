"""Document chunking service using Docling's hybrid chunker."""

from dataclasses import dataclass
from typing import Any

from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer


EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_MAX_TOKENS = 512


@dataclass
class ChunkResult:
    """Result of chunking a document."""

    text: str
    context: str
    chunk_index: int
    page_number: int | None
    section_title: str | None
    token_count: int
    metadata: dict


def create_chunker(
    model_id: str = EMBED_MODEL_ID,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> HybridChunker:
    """Create a configured HybridChunker instance."""
    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(model_id),
        max_tokens=max_tokens,
    )
    return HybridChunker(tokenizer=tokenizer)


def chunk_document(
    document: Any,
    model_id: str = EMBED_MODEL_ID,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> list[ChunkResult]:
    """
    Chunk a Docling document into smaller pieces for RAG.
    
    Args:
        document: A DoclingDocument from the converter
        model_id: Embedding model ID for tokenizer
        max_tokens: Maximum tokens per chunk
        
    Returns:
        List of ChunkResult objects
    """
    chunker = create_chunker(model_id, max_tokens)
    tokenizer = chunker.tokenizer
    
    chunks = list(chunker.chunk(document))
    results = []
    
    for i, chunk in enumerate(chunks):
        text = chunk.text
        context = chunker.contextualize(chunk)
        token_count = tokenizer.count_tokens(text)
        
        page_number = None
        section_title = None
        
        if hasattr(chunk, 'meta') and chunk.meta:
            meta = chunk.meta
            if hasattr(meta, 'doc_items') and meta.doc_items:
                first_item = meta.doc_items[0]
                if hasattr(first_item, 'prov') and first_item.prov:
                    prov = first_item.prov[0] if first_item.prov else None
                    if prov and hasattr(prov, 'page_no'):
                        page_number = prov.page_no
            
            if hasattr(meta, 'headings') and meta.headings:
                section_title = meta.headings[-1] if meta.headings else None
        
        results.append(ChunkResult(
            text=text,
            context=context,
            chunk_index=i,
            page_number=page_number,
            section_title=section_title,
            token_count=token_count,
            metadata={
                "model_id": model_id,
                "max_tokens": max_tokens,
            },
        ))
    
    return results
