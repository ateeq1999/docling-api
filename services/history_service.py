"""Document history service."""

from typing import Literal

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Document


async def save_document_record(
    db: AsyncSession,
    filename: str,
    file_size: int,
    file_type: str,
    output_format: str,
    status: Literal["success", "error"] = "success",
    page_count: int | None = None,
    processing_time_ms: int | None = None,
    error_message: str | None = None,
) -> Document:
    """Save a document processing record to the database."""
    doc = Document(
        filename=filename,
        file_size=file_size,
        file_type=file_type,
        output_format=output_format,
        status=status,
        page_count=page_count,
        processing_time_ms=processing_time_ms,
        error_message=error_message,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def get_document_history(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> list[Document]:
    """Get document processing history."""
    result = await db.execute(
        select(Document).order_by(desc(Document.created_at)).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def get_document_stats(db: AsyncSession) -> dict:
    """Get document processing statistics."""
    result = await db.execute(select(Document))
    documents = list(result.scalars().all())

    total = len(documents)
    successful = sum(1 for d in documents if d.status == "success")
    failed = sum(1 for d in documents if d.status == "error")
    total_size = sum(d.file_size for d in documents)

    return {
        "total_documents": total,
        "successful": successful,
        "failed": failed,
        "total_size_bytes": total_size,
        "success_rate": round(successful / total * 100, 1) if total > 0 else 0,
    }


def get_file_type(filename: str) -> str:
    """Extract file type from filename."""
    if not filename:
        return "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"
    return ext
