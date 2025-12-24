from typing import AsyncGenerator
import asyncio
import json
import tempfile
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile, HTTPException
from docling.document_converter import DocumentConverter
from docling.exceptions import ConversionError

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
            raise HTTPException(status_code=413, detail="File too large")

    await file.seek(0)


# -------------------------
# Blocking conversion
# -------------------------

def _convert(path: Path, output_format: str) -> str:
    converter = DocumentConverter()

    try:
        result = converter.convert(str(path))
    except ConversionError as e:
        raise ValueError(f"Invalid or unsupported document: {e}")  # FIX

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
# Non-streaming API
# -------------------------

async def process_document(
    file: UploadFile,
    output_format: str,
) -> Tuple[str, str]:

    await validate_file_size(file)

    # FIX: create temp file manually and CLOSE it before conversion
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp_path = Path(tmp.name)

    try:
        while chunk := await file.read(1024 * 1024):
            tmp.write(chunk)

        tmp.close()  # 🔥 CRITICAL FIX FOR WINDOWS

        try:
            content = await asyncio.to_thread(
                _convert,
                tmp_path,
                output_format,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        media_type = (
            "application/json"
            if output_format == "json"
            else "text/plain"
        )

        return content, media_type

    finally:
        # FIX: delete ONLY after conversion completes
        try:
            tmp_path.unlink()
        except Exception:
            pass


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

# ----------------------------------
# Per-page streaming
# ----------------------------------

async def process_document_per_page_stream(
    file: UploadFile,
    output_format: str,
) -> AsyncGenerator[bytes, None]:

    # size check
    size = 0
    while chunk := await file.read(1024 * 1024):
        size += len(chunk)
        if size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(413, "File too large")

    await file.seek(0)

    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = Path(tmp.name)

    try:
        while chunk := await file.read(1024 * 1024):
            tmp.write(chunk)
        tmp.close()

        def _load():
            converter = DocumentConverter()
            return converter.convert(str(path)).document

        try:
            document = await asyncio.to_thread(_load)
        except ConversionError as e:
            raise HTTPException(422, str(e))

        for idx, page in enumerate(document.pages, start=1):
            if output_format == "text":
                content = page.export_to_text()
            elif output_format == "markdown":
                content = page.export_to_markdown()
            else:
                content = json.dumps(page.export_to_json())

            payload = {
                "page": idx,
                "content": content,
            }

            yield (json.dumps(payload) + "\n").encode()
            await asyncio.sleep(0)

    finally:
        path.unlink(missing_ok=True)

async def process_document_sse(
    file: UploadFile,
    output_format: str,
) -> AsyncGenerator[str, None]:

    yield "event: status\ndata: Upload received\n\n"

    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = Path(tmp.name)

    try:
        yield "event: status\ndata: Saving file\n\n"

        while chunk := await file.read(1024 * 1024):
            tmp.write(chunk)

        tmp.close()

        yield "event: status\ndata: Converting document\n\n"

        def _convert():
            converter = DocumentConverter()
            return converter.convert(str(path)).document

        try:
            doc = await asyncio.to_thread(_convert)
        except ConversionError as e:
            yield f"event: error\ndata: {str(e)}\n\n"
            return

        yield "event: status\ndata: Exporting content\n\n"

        content = (
            doc.export_to_markdown()
            if output_format == "markdown"
            else doc.export_to_text()
        )

        yield f"event: result\ndata: {content}\n\n"
        yield "event: done\ndata: Completed\n\n"

    finally:
        path.unlink(missing_ok=True)

async def process_bulk_documents(
    files: list[UploadFile],
    output_format: str,
) -> list[dict]:

    results = []

    for file in files:
        try:
            content, _ = await process_document(file, output_format)
            results.append({
                "filename": file.filename,
                "status": "success",
                "content": content,
            })
        except HTTPException as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": e.detail,
            })

    return results

async def load_document(file: UploadFile):
    import asyncio, tempfile
    from pathlib import Path
    from docling.document_converter import DocumentConverter
    from docling.exceptions import ConversionError

    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = Path(tmp.name)

    try:
        while chunk := await file.read(1024 * 1024):
            tmp.write(chunk)
        tmp.close()

        def _load():
            return DocumentConverter().convert(str(path)).document

        return await asyncio.to_thread(_load)

    finally:
        path.unlink(missing_ok=True)
