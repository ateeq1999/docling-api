"""Document processing endpoints."""

from fastapi import APIRouter, Query, UploadFile
from fastapi.responses import Response, StreamingResponse

from core.schemas import BulkDocumentResult
from services.docling_converter import OutputFormat
from services.docling_service import (
    process_bulk_documents,
    process_document,
    process_document_per_page_stream,
    process_document_sse,
    process_document_stream,
)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post("/process", response_class=Response)
async def process(
    file: UploadFile,
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
):
    """Convert a document to the specified format."""
    content, media_type = await process_document(file=file, output_format=format)
    return Response(content=content, media_type=media_type)


@router.post("/process/stream")
async def process_stream(
    file: UploadFile,
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
):
    """Convert a document and stream the response."""
    stream, media_type = await process_document_stream(file=file, output_format=format)
    return StreamingResponse(stream, media_type=media_type)


@router.post("/process/stream/pages")
async def process_stream_pages(
    file: UploadFile,
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
):
    """Convert a document and stream content page by page as JSON lines."""
    return StreamingResponse(
        process_document_per_page_stream(file, format),
        media_type="application/x-ndjson",
    )


@router.post("/process/sse")
async def process_sse(
    file: UploadFile,
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
):
    """Convert a document and stream progress as Server-Sent Events."""
    return StreamingResponse(
        process_document_sse(file, format),
        media_type="text/event-stream",
    )


@router.post("/process/bulk", response_model=list[BulkDocumentResult])
async def process_bulk(
    files: list[UploadFile],
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
):
    """Process multiple documents concurrently."""
    return await process_bulk_documents(files, format)
