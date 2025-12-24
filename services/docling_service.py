import asyncio
import json
import tempfile
from pathlib import Path
from typing import AsyncGenerator

from fastapi import UploadFile, HTTPException
from docling.document_converter import DocumentConverter

from app.core.config import MAX_FILE_SIZE_BYTES


# -------------------------
# File size validation
# -------------------------

async def validate_file_size(file: UploadFile) -> None:
    size = 0
    chunk_size = 1024 * 1024

    while chunk := await file.read(chunk_size):
        size += len(chunk)
        if size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="Uploaded file exceeds size limit",
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

    raise ValueError("Unsupported output format")


# -------------------------
# Streaming generator
# -------------------------

async def stream_text(content: str) -> AsyncGenerator[bytes, None]:
    chunk = 2048
    for i in range(0, len(content), chunk):
        yield content[i : i + chunk].encode()
        await asyncio.sleep(0)


# -------------------------
# Public service API
# -------------------------

async def process_document_stream(
    file: UploadFile,
    output_format: str,
):
    """
    Accepts ANY input Docling can handle (docs, images, binaries).
    """

    await validate_file_size(file)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)

        try:
            while chunk := await file.read(1024 * 1024):
                tmp.write(chunk)

            content = await asyncio.to_thread(
                _convert,
                tmp_path,
                output_format,
            )

            media_type = (
                "application/json"
                if output_format == "json"
                else "text/plain"
            )

            return stream_text(content), media_type

        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
