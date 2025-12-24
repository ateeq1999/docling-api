from fastapi import APIRouter, UploadFile, Query
from fastapi.responses import StreamingResponse, Response
from services.image_service import extract_images_with_annotations

from services.docling_service import (
    process_document,
    process_document_stream,
    process_document_per_page_stream,
    process_document_sse,
    process_bulk_documents,
    load_document,
)

router = APIRouter()


# -------------------------
# Non-streaming endpoint
# -------------------------

@router.post("/process")
async def process(
    file: UploadFile,
    format: str = Query("markdown", enum=["text", "markdown", "json"]),
):
    content, media_type = await process_document(
        file=file,
        output_format=format,
    )

    return Response(
        content=content,
        media_type=media_type,
    )


# -------------------------
# Streaming endpoint
# -------------------------

@router.post("/process/stream")
async def process_stream(
    file: UploadFile,
    format: str = Query("markdown", enum=["text", "markdown", "json"]),
):
    stream, media_type = await process_document_stream(
        file=file,
        output_format=format,
    )

    return StreamingResponse(
        stream,
        media_type=media_type,
    )

@router.post("/process/stream/pages")
async def process_stream_pages(
    file: UploadFile,
    format: str = Query("markdown", enum=["text", "markdown", "json"]),
):
    return StreamingResponse(
        process_document_per_page_stream(file, format),
        media_type="application/json",
    )

@router.post("/process/sse")
async def process_sse(
    file: UploadFile,
    format: str = Query("markdown"),
):
    return StreamingResponse(
        process_document_sse(file, format),
        media_type="text/event-stream",
    )

@router.post("/process/bulk")
async def process_bulk(
    files: list[UploadFile],
    format: str = Query("markdown"),
):
    return await process_bulk_documents(files, format)

@router.post("/process/images")
async def extract_images(file: UploadFile):
    document = await load_document(file)

    images = extract_images_with_annotations(document)

    return {
        "count": len(images),
        "images": images,
    }
