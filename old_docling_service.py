import asyncio
import json
import os
from pathlib import Path
from typing import Any

from fastapi import UploadFile, HTTPException
from docling.document_converter import DocumentConverter


# -----------------------------
# Allowed file types
# -----------------------------

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


# -----------------------------
# OCR / Layout configuration
# (Docling-supported way)
# -----------------------------

os.environ.setdefault("DOCLING_OCR_BACKEND", "tesseract")
os.environ.setdefault("DOCLING_OCR_LANGS", "eng")
os.environ.setdefault("DOCLING_LAYOUT_BACKEND", "default")


# -----------------------------
# Validation
# -----------------------------

def validate_upload(file: UploadFile) -> None:
    ext = Path(file.filename).suffix.lower()

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported MIME type: {file.content_type}",
        )

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file extension: {ext}",
        )


# -----------------------------
# Blocking Docling execution
# -----------------------------

def _convert_document(file_path: Path, output_format: str) -> Any:
    converter = DocumentConverter()
    result = converter.convert(str(file_path))
    document = result.document

    if output_format == "text":
        return document.export_to_text()

    if output_format == "markdown":
        return document.export_to_markdown()

    if output_format == "json":
        data = document.export_to_json()
        return json.loads(data) if isinstance(data, str) else data

    raise ValueError(f"Unsupported output format: {output_format}")


# -----------------------------
# Async-safe public API
# -----------------------------

async def process_document_async(
    file: UploadFile,
    saved_path: Path,
    output_format: str,
) -> Any:
    """
    Async-safe wrapper for FastAPI
    """

    validate_upload(file)

    return await asyncio.to_thread(
        _convert_document,
        saved_path,
        output_format,
    )
