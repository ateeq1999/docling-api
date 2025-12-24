"""In-memory caching utilities."""

import hashlib
from functools import wraps
from typing import Callable

from cachetools import LRUCache, TTLCache

embedding_cache: TTLCache = TTLCache(maxsize=1000, ttl=3600)

search_cache: TTLCache = TTLCache(maxsize=500, ttl=300)

llm_cache: LRUCache = LRUCache(maxsize=200)


def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from arguments."""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cached_embedding(func: Callable) -> Callable:
    """Decorator for caching embedding results."""

    @wraps(func)
    def wrapper(self, texts: list[str]) -> list[list[float]]:
        results = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            key = cache_key(text, self.model_id if hasattr(self, "model_id") else "default")
            if key in embedding_cache:
                results.append((i, embedding_cache[key]))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        if uncached_texts:
            new_embeddings = func(self, uncached_texts)
            for idx, emb in zip(uncached_indices, new_embeddings):
                text = texts[idx]
                key = cache_key(text, self.model_id if hasattr(self, "model_id") else "default")
                embedding_cache[key] = emb
                results.append((idx, emb))

        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]

    return wrapper


def get_cached_search(query: str, doc_ids: tuple | None, top_k: int) -> list | None:
    """Get cached search results."""
    key = cache_key(query, doc_ids, top_k)
    return search_cache.get(key)


def set_cached_search(
    query: str,
    doc_ids: tuple | None,
    top_k: int,
    results: list,
) -> None:
    """Cache search results."""
    key = cache_key(query, doc_ids, top_k)
    search_cache[key] = results


def get_cached_llm(prompt: str, context_hash: str) -> str | None:
    """Get cached LLM response."""
    key = cache_key(prompt, context_hash)
    return llm_cache.get(key)


def set_cached_llm(prompt: str, context_hash: str, response: str) -> None:
    """Cache LLM response."""
    key = cache_key(prompt, context_hash)
    llm_cache[key] = response


def clear_caches() -> dict:
    """Clear all caches and return stats."""
    stats = {
        "embedding_cache_cleared": len(embedding_cache),
        "search_cache_cleared": len(search_cache),
        "llm_cache_cleared": len(llm_cache),
    }
    embedding_cache.clear()
    search_cache.clear()
    llm_cache.clear()
    return stats


def get_cache_stats() -> dict:
    """Get current cache statistics."""
    return {
        "embedding_cache": {
            "size": len(embedding_cache),
            "maxsize": embedding_cache.maxsize,
            "ttl": embedding_cache.ttl,
        },
        "search_cache": {
            "size": len(search_cache),
            "maxsize": search_cache.maxsize,
            "ttl": search_cache.ttl,
        },
        "llm_cache": {
            "size": len(llm_cache),
            "maxsize": llm_cache.maxsize,
        },
    }
