"""Extracted images endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Document, ExtractedImage

router = APIRouter(
    prefix="/extracted-images",
    tags=["images"],
)


class ExtractedImageResponse(BaseModel):
    id: int
    document_id: int
    image_index: int
    page_number: int | None
    image_type: str
    width: int
    height: int
    file_path: str
    caption: str | None
    description: str | None
    has_embedding: bool
    created_at: str | None


@router.get("/document/{document_id}", response_model=list[ExtractedImageResponse])
async def get_document_images(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all images extracted from a document."""
    doc_result = await db.execute(select(Document).where(Document.id == document_id))
    if not doc_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")

    result = await db.execute(
        select(ExtractedImage)
        .where(ExtractedImage.document_id == document_id)
        .order_by(ExtractedImage.image_index)
    )
    images = result.scalars().all()

    return [
        ExtractedImageResponse(
            id=img.id,
            document_id=img.document_id,
            image_index=img.image_index,
            page_number=img.page_number,
            image_type=img.image_type,
            width=img.width,
            height=img.height,
            file_path=img.file_path,
            caption=img.caption,
            description=img.description,
            has_embedding=bool(img.has_embedding),
            created_at=img.created_at.isoformat() if img.created_at else None,
        )
        for img in images
    ]


@router.get("/{image_id}", response_model=ExtractedImageResponse)
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single image by ID."""
    result = await db.execute(
        select(ExtractedImage).where(ExtractedImage.id == image_id)
    )
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return ExtractedImageResponse(
        id=image.id,
        document_id=image.document_id,
        image_index=image.image_index,
        page_number=image.page_number,
        image_type=image.image_type,
        width=image.width,
        height=image.height,
        file_path=image.file_path,
        caption=image.caption,
        description=image.description,
        has_embedding=bool(image.has_embedding),
        created_at=image.created_at.isoformat() if image.created_at else None,
    )


@router.get("/{image_id}/file")
async def get_image_file(
    image_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get the actual image file."""
    result = await db.execute(
        select(ExtractedImage).where(ExtractedImage.id == image_id)
    )
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    import os
    if not os.path.exists(image.file_path):
        raise HTTPException(status_code=404, detail="Image file not found")

    return FileResponse(image.file_path, media_type="image/png")
