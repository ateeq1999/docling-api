import asyncio
import json
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Tuple

from fastapi import UploadFile, HTTPException
from docling.document_converter import DocumentConverter

from core.config import MAX_FILE_SIZE_BYTES


# -------------------------
# File size validation
# -------------------------

async def validate_file_size(file: UploadFile) -> None:
    size = 0
    chunk = 1024 * 1024

    while data := await file.read(chunk):
        size += len(data)
        if size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File too large",
            )

    await file.seek(0)


# -------------------------
# Blocking Docling execution
# -------------------------

def _convert(path: Path, output_format: str) -> str:
    converter = DocumentConverter()
    result = converter.convert(str(path))
    doc = result.document

    if output_format == "text":
        return doc.export_to_text()

    if output_format == "markdown":
        return doc.export_to_markdown()

    if output_format == "json":
        data = doc.export_to_json()
        return json.dumps(data) if not isinstance(data, str) else data

    raise ValueError("Unsupported format")


# -------------------------
# Streaming generator
# -------------------------

async def stream_text(content: str) -> AsyncGenerator[bytes, None]:
    size = 2048
    for i in range(0, len(content), size):
        yield content[i : i + size].encode()
        await asyncio.sleep(0)


# -------------------------
# Non-streaming API
# -------------------------

async def process_document(
    file: UploadFile,
    output_format: str,
) -> Tuple[str, str]:
    """
    Returns full content (non-streaming)
    """

    await validate_file_size(file)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        path = Path(tmp.name)

        try:
            while chunk := await file.read(1024 * 1024):
                tmp.write(chunk)

            content = await asyncio.to_thread(
                _convert,
                path,
                output_format,
            )

            media_type = (
                "application/json"
                if output_format == "json"
                else "text/plain"
            )

            return content, media_type

        finally:
            path.unlink(missing_ok=True)


# -------------------------
# Streaming API
# -------------------------

async def process_document_stream(
    file: UploadFile,
    output_format: str,
) -> Tuple[AsyncGenerator[bytes, None], str]:
    """
    Streams content progressively
    """

    content, media_type = await process_document(
        file=file,
        output_format=output_format,
    )

    return stream_text(content), media_type
