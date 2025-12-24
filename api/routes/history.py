"""Document history endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.history_service import get_document_history, get_document_stats

router = APIRouter(
    prefix="/history",
    tags=["history"],
)


@router.get("/")
async def list_history(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Get document processing history."""
    documents = await get_document_history(db, limit=limit, offset=offset)
    return {"documents": [doc.to_dict() for doc in documents]}


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get document processing statistics."""
    return await get_document_stats(db)
