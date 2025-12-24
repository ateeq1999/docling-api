"""File utilities for handling uploads and temporary files."""

import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import HTTPException, UploadFile

from core.config import MAX_FILE_SIZE_BYTES

CHUNK_SIZE = 1024 * 1024  # 1 MB


@asynccontextmanager
async def save_upload_to_tempfile(file: UploadFile) -> AsyncIterator[Path]:
    """
    Save an uploaded file to a temporary file with size validation.
    
    Automatically cleans up the temp file when the context exits.
    """
    size = 0
    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = Path(tmp.name)

    try:
        while chunk := await file.read(CHUNK_SIZE):
            size += len(chunk)
            if size > MAX_FILE_SIZE_BYTES:
                raise HTTPException(status_code=413, detail="File too large")
            tmp.write(chunk)

        tmp.close()
        await file.seek(0)
        yield path

    finally:
        path.unlink(missing_ok=True)


async def validate_file_size(file: UploadFile) -> None:
    """Validate file size without saving to disk."""
    size = 0

    while data := await file.read(CHUNK_SIZE):
        size += len(data)
        if size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="File too large")

    await file.seek(0)
