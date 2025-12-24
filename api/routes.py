from fastapi import APIRouter, UploadFile, Query
from fastapi.responses import StreamingResponse, Response

from services.docling_service import (
    process_document,
    process_document_stream,
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
