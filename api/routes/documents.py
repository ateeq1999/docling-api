"""Document processing endpoints."""

import time

from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.schemas import BulkDocumentResult
from services.docling_converter import OutputFormat
from services.docling_service import (
    process_bulk_documents,
    process_document,
    process_document_per_page_stream,
    process_document_sse,
    process_document_stream,
)
from services.history_service import get_file_type, save_document_record

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.post("/process", response_class=Response)
async def process(
    file: UploadFile,
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
    db: AsyncSession = Depends(get_db),
):
    """Convert a document to the specified format."""
    start_time = time.time()
    file_size = 0

    file_content = await file.read()
    file_size = len(file_content)
    await file.seek(0)

    try:
        content, media_type = await process_document(file=file, output_format=format)
        processing_time = int((time.time() - start_time) * 1000)

        await save_document_record(
            db=db,
            filename=file.filename or "unknown",
            file_size=file_size,
            file_type=get_file_type(file.filename or ""),
            output_format=format.value,
            status="success",
            processing_time_ms=processing_time,
        )

        return Response(content=content, media_type=media_type)
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        await save_document_record(
            db=db,
            filename=file.filename or "unknown",
            file_size=file_size,
            file_type=get_file_type(file.filename or ""),
            output_format=format.value,
            status="error",
            processing_time_ms=processing_time,
            error_message=str(e),
        )
        raise


@router.post("/process/stream")
async def process_stream(
    file: UploadFile,
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
    db: AsyncSession = Depends(get_db),
):
    """Convert a document and stream the response."""
    file_content = await file.read()
    file_size = len(file_content)
    await file.seek(0)

    await save_document_record(
        db=db,
        filename=file.filename or "unknown",
        file_size=file_size,
        file_type=get_file_type(file.filename or ""),
        output_format=format.value,
        status="success",
    )

    stream, media_type = await process_document_stream(file=file, output_format=format)
    return StreamingResponse(stream, media_type=media_type)


@router.post("/process/stream/pages")
async def process_stream_pages(
    file: UploadFile,
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
    db: AsyncSession = Depends(get_db),
):
    """Convert a document and stream content page by page as JSON lines."""
    file_content = await file.read()
    file_size = len(file_content)
    await file.seek(0)

    await save_document_record(
        db=db,
        filename=file.filename or "unknown",
        file_size=file_size,
        file_type=get_file_type(file.filename or ""),
        output_format=format.value,
        status="success",
    )

    return StreamingResponse(
        process_document_per_page_stream(file, format),
        media_type="application/x-ndjson",
    )


@router.post("/process/sse")
async def process_sse(
    file: UploadFile,
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
    db: AsyncSession = Depends(get_db),
):
    """Convert a document and stream progress as Server-Sent Events."""
    file_content = await file.read()
    file_size = len(file_content)
    await file.seek(0)

    await save_document_record(
        db=db,
        filename=file.filename or "unknown",
        file_size=file_size,
        file_type=get_file_type(file.filename or ""),
        output_format=format.value,
        status="success",
    )

    return StreamingResponse(
        process_document_sse(file, format),
        media_type="text/event-stream",
    )


@router.post("/process/bulk", response_model=list[BulkDocumentResult])
async def process_bulk(
    files: list[UploadFile],
    format: OutputFormat = Query(OutputFormat.MARKDOWN),
    db: AsyncSession = Depends(get_db),
):
    """Process multiple documents concurrently."""
    for file in files:
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)

        await save_document_record(
            db=db,
            filename=file.filename or "unknown",
            file_size=file_size,
            file_type=get_file_type(file.filename or ""),
            output_format=format.value,
            status="success",
        )

    return await process_bulk_documents(files, format)
