"""API routes package."""

from fastapi import APIRouter

from .documents import router as documents_router
from .health import router as health_router
from .images import router as images_router

router = APIRouter()

router.include_router(documents_router)
router.include_router(images_router)
router.include_router(health_router)

__all__ = ["router"]
