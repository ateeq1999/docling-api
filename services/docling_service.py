"""High-level document processing orchestration."""

import asyncio
from typing import Any, AsyncIterator

from fastapi import HTTPException, UploadFile
from docling.exceptions import ConversionError

from core.schemas import BulkDocumentResult
from .docling_converter import (
    OutputFormat,
    convert_file,
    get_media_type,
    load_document_from_path,
)
from .docling_streaming import stream_pages, stream_sse_events, stream_text
from .file_utils import save_upload_to_tempfile


async def process_document(
    file: UploadFile,
    output_format: OutputFormat,
) -> tuple[str, str]:
    """Process a single document and return content with media type."""
    async with save_upload_to_tempfile(file) as tmp_path:
        try:
            content = await asyncio.to_thread(convert_file, tmp_path, output_format)
        except ConversionError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    return content, get_media_type(output_format)


async def process_document_stream(
    file: UploadFile,
    output_format: OutputFormat,
) -> tuple[AsyncIterator[bytes], str]:
    """Process a document and return a streaming response."""
    content, media_type = await process_document(file=file, output_format=output_format)
    return stream_text(content), media_type


async def process_document_per_page_stream(
    file: UploadFile,
    output_format: OutputFormat,
) -> AsyncIterator[bytes]:
    """Process a document and stream content page by page."""
    async with save_upload_to_tempfile(file) as tmp_path:
        try:
            document = await asyncio.to_thread(load_document_from_path, tmp_path)
        except ConversionError as e:
            raise HTTPException(status_code=422, detail=str(e))

        async for chunk in stream_pages(document, output_format):
            yield chunk


async def process_document_sse(
    file: UploadFile,
    output_format: OutputFormat,
) -> AsyncIterator[str]:
    """Process a document and stream content as Server-Sent Events."""
    yield "event: status\ndata: Upload received\n\n"
    yield "event: status\ndata: Saving file\n\n"

    async with save_upload_to_tempfile(file) as tmp_path:
        yield "event: status\ndata: Converting document\n\n"

        try:
            document = await asyncio.to_thread(load_document_from_path, tmp_path)
        except ConversionError as e:
            yield f"event: error\ndata: {e}\n\n"
            return

        async for event in stream_sse_events(document, output_format):
            yield event


async def process_bulk_documents(
    files: list[UploadFile],
    output_format: OutputFormat,
    max_concurrency: int = 4,
) -> list[BulkDocumentResult]:
    """Process multiple documents concurrently with a concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrency)
    results: list[BulkDocumentResult] = []

    async def handle_file(file: UploadFile) -> BulkDocumentResult:
        async with semaphore:
            try:
                content, _ = await process_document(file, output_format)
                return BulkDocumentResult(
                    filename=file.filename,
                    status="success",
                    content=content,
                )
            except HTTPException as e:
                return BulkDocumentResult(
                    filename=file.filename,
                    status="error",
                    error=str(e.detail),
                )

    tasks = [handle_file(f) for f in files]
    results = await asyncio.gather(*tasks)
    return list(results)


async def load_document(file: UploadFile) -> Any:
    """Load a document from an uploaded file."""
    async with save_upload_to_tempfile(file) as tmp_path:
        try:
            return await asyncio.to_thread(load_document_from_path, tmp_path)
        except ConversionError as e:
            raise HTTPException(status_code=422, detail=str(e))
