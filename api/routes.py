from fastapi import APIRouter, UploadFile, Query
from fastapi.responses import StreamingResponse

from app.services.docling_service import process_document_stream

router = APIRouter()


@router.post("/process")
async def process_document(
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
