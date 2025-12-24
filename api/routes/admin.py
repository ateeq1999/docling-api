"""Admin endpoints for cache and job management."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.auth import get_current_user
from core.cache import clear_caches, get_cache_stats
from core.models import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


class CacheStatsResponse(BaseModel):
    embedding_cache: dict
    search_cache: dict
    llm_cache: dict


class ClearCacheResponse(BaseModel):
    embedding_cache_cleared: int
    search_cache_cleared: int
    llm_cache_cleared: int


def require_admin(user: User = Depends(get_current_user)):
    """Require admin privileges."""
    if user is None:
        return None
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def cache_stats():
    """Get cache statistics."""
    stats = get_cache_stats()
    return CacheStatsResponse(**stats)


@router.post("/cache/clear", response_model=ClearCacheResponse)
async def clear_cache():
    """Clear all caches."""
    result = clear_caches()
    return ClearCacheResponse(**result)


@router.get("/health/detailed")
async def detailed_health():
    """Get detailed health information."""
    from core.vector_store import get_vector_store

    try:
        vector_store = get_vector_store()
        vector_count = vector_store.count()
    except Exception:
        vector_count = -1

    cache_stats = get_cache_stats()

    return {
        "status": "healthy",
        "vector_store": {
            "type": "sqlite-vec",
            "count": vector_count,
        },
        "cache": cache_stats,
    }
