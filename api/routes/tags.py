"""Tag management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Document, DocumentTag, Tag

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)


class CreateTagRequest(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str
    document_count: int
    created_at: str | None


class TagDocumentsRequest(BaseModel):
    tag_ids: list[int]


@router.post("", response_model=TagResponse)
async def create_tag(
    request: CreateTagRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new tag."""
    existing = await db.execute(select(Tag).where(Tag.name == request.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tag already exists")

    tag = Tag(name=request.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return TagResponse(
        id=tag.id,
        name=tag.name,
        document_count=0,
        created_at=tag.created_at.isoformat() if tag.created_at else None,
    )


@router.get("", response_model=list[TagResponse])
async def list_tags(
    db: AsyncSession = Depends(get_db),
):
    """List all tags."""
    result = await db.execute(select(Tag).order_by(Tag.name))
    tags = result.scalars().all()

    responses = []
    for t in tags:
        doc_count_result = await db.execute(
            select(DocumentTag).where(DocumentTag.tag_id == t.id)
        )
        doc_count = len(doc_count_result.scalars().all())

        responses.append(TagResponse(
            id=t.id,
            name=t.name,
            document_count=doc_count,
            created_at=t.created_at.isoformat() if t.created_at else None,
        ))

    return responses


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a tag."""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await db.delete(tag)
    await db.commit()

    return {"status": "deleted", "tag_id": tag_id}


@router.post("/documents/{document_id}")
async def tag_document(
    document_id: int,
    request: TagDocumentsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add tags to a document."""
    doc_result = await db.execute(select(Document).where(Document.id == document_id))
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    added = []
    for tag_id in request.tag_ids:
        tag_result = await db.execute(select(Tag).where(Tag.id == tag_id))
        tag = tag_result.scalar_one_or_none()
        if not tag:
            continue

        existing = await db.execute(
            select(DocumentTag).where(
                DocumentTag.document_id == document_id,
                DocumentTag.tag_id == tag_id,
            )
        )
        if existing.scalar_one_or_none():
            continue

        dt = DocumentTag(document_id=document_id, tag_id=tag_id)
        db.add(dt)
        added.append(tag_id)

    await db.commit()

    return {"document_id": document_id, "tags_added": added}


@router.get("/documents/{document_id}")
async def get_document_tags(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all tags for a document."""
    doc_result = await db.execute(select(Document).where(Document.id == document_id))
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    tags_result = await db.execute(
        select(Tag)
        .join(DocumentTag, DocumentTag.tag_id == Tag.id)
        .where(DocumentTag.document_id == document_id)
    )
    tags = tags_result.scalars().all()

    return {
        "document_id": document_id,
        "tags": [t.to_dict() for t in tags],
    }


@router.delete("/documents/{document_id}/{tag_id}")
async def untag_document(
    document_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Remove a tag from a document."""
    result = await db.execute(
        select(DocumentTag).where(
            DocumentTag.document_id == document_id,
            DocumentTag.tag_id == tag_id,
        )
    )
    dt = result.scalar_one_or_none()

    if not dt:
        raise HTTPException(status_code=404, detail="Tag not on document")

    await db.delete(dt)
    await db.commit()

    return {"status": "removed", "document_id": document_id, "tag_id": tag_id}
