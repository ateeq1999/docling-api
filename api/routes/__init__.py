"""API routes package."""

from fastapi import APIRouter

from .chat import router as chat_router
from .chunks import router as chunks_router
from .collections import router as collections_router
from .documents import router as documents_router
from .extracted_images import router as extracted_images_router
from .health import router as health_router
from .history import router as history_router
from .images import router as images_router
from .search import router as search_router
from .tables import router as tables_router
from .tags import router as tags_router

router = APIRouter()

router.include_router(documents_router)
router.include_router(images_router)
router.include_router(health_router)
router.include_router(history_router)
router.include_router(chunks_router)
router.include_router(search_router)
router.include_router(chat_router)
router.include_router(collections_router)
router.include_router(tags_router)
router.include_router(tables_router)
router.include_router(extracted_images_router)

__all__ = ["router"]
