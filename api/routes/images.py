"""Image extraction endpoints."""

from fastapi import APIRouter, UploadFile

from core.schemas import ImagesResponse
from services.docling_service import load_document
from services.image_service import extract_images_with_annotations

router = APIRouter(
    prefix="/images",
    tags=["images"],
)


@router.post("/extract", response_model=ImagesResponse)
async def extract_images(file: UploadFile):
    """Extract images and page renders from a document."""
    document = await load_document(file)
    images = extract_images_with_annotations(document)

    return ImagesResponse(
        count=len(images),
        images=images,
    )
