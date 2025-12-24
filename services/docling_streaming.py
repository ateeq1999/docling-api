"""Streaming utilities for document content."""

import asyncio
import json
from typing import Any, AsyncIterator

from .docling_converter import OutputFormat

STREAM_CHUNK_SIZE = 4096


async def stream_text(text: str, chunk_size: int = STREAM_CHUNK_SIZE) -> AsyncIterator[bytes]:
    """Stream text content in chunks."""
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size].encode("utf-8")
        await asyncio.sleep(0)


async def stream_pages(
    document: Any,
    output_format: OutputFormat,
) -> AsyncIterator[bytes]:
    """Stream document content page by page as JSON lines."""
    for page_idx, page in document.pages.items():
        if output_format is OutputFormat.TEXT:
            content = page.export_to_text()
        elif output_format is OutputFormat.MARKDOWN:
            content = page.export_to_markdown()
        else:
            content = json.dumps(page.export_to_dict())

        payload = {
            "page": page_idx,
            "content": content,
        }

        yield (json.dumps(payload) + "\n").encode("utf-8")
        await asyncio.sleep(0)


async def stream_sse_events(
    document: Any,
    output_format: OutputFormat,
) -> AsyncIterator[str]:
    """Stream document content as Server-Sent Events."""
    yield "event: status\ndata: Exporting content\n\n"

    content = (
        document.export_to_markdown()
        if output_format is OutputFormat.MARKDOWN
        else document.export_to_text()
    )

    yield f"event: result\ndata: {content}\n\n"
    yield "event: done\ndata: Completed\n\n"
