"""Collection management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import Collection, CollectionDocument, Document

router = APIRouter(
    prefix="/collections",
    tags=["collections"],
)


class CreateCollectionRequest(BaseModel):
    name: str
    description: str | None = None


class CollectionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    document_count: int
    created_at: str | None


class AddDocumentsRequest(BaseModel):
    document_ids: list[int]


@router.post("", response_model=CollectionResponse)
async def create_collection(
    request: CreateCollectionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new collection."""
    collection = Collection(name=request.name, description=request.description)
    db.add(collection)
    await db.commit()
    await db.refresh(collection)

    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        document_count=0,
        created_at=collection.created_at.isoformat() if collection.created_at else None,
    )


@router.get("", response_model=list[CollectionResponse])
async def list_collections(
    db: AsyncSession = Depends(get_db),
):
    """List all collections."""
    result = await db.execute(
        select(Collection).order_by(Collection.created_at.desc())
    )
    collections = result.scalars().all()

    responses = []
    for c in collections:
        doc_count_result = await db.execute(
            select(CollectionDocument).where(CollectionDocument.collection_id == c.id)
        )
        doc_count = len(doc_count_result.scalars().all())

        responses.append(CollectionResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            document_count=doc_count,
            created_at=c.created_at.isoformat() if c.created_at else None,
        ))

    return responses


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a collection by ID."""
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    doc_count_result = await db.execute(
        select(CollectionDocument).where(CollectionDocument.collection_id == collection_id)
    )
    doc_count = len(doc_count_result.scalars().all())

    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        document_count=doc_count,
        created_at=collection.created_at.isoformat() if collection.created_at else None,
    )


@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a collection."""
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    await db.delete(collection)
    await db.commit()

    return {"status": "deleted", "collection_id": collection_id}


@router.post("/{collection_id}/documents")
async def add_documents_to_collection(
    collection_id: int,
    request: AddDocumentsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add documents to a collection."""
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    added = []
    for doc_id in request.document_ids:
        doc_result = await db.execute(
            select(Document).where(Document.id == doc_id)
        )
        doc = doc_result.scalar_one_or_none()
        if not doc:
            continue

        existing = await db.execute(
            select(CollectionDocument).where(
                CollectionDocument.collection_id == collection_id,
                CollectionDocument.document_id == doc_id,
            )
        )
        if existing.scalar_one_or_none():
            continue

        cd = CollectionDocument(collection_id=collection_id, document_id=doc_id)
        db.add(cd)
        added.append(doc_id)

    await db.commit()

    return {"added": added, "collection_id": collection_id}


@router.get("/{collection_id}/documents")
async def get_collection_documents(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all documents in a collection."""
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    docs_result = await db.execute(
        select(Document)
        .join(CollectionDocument, CollectionDocument.document_id == Document.id)
        .where(CollectionDocument.collection_id == collection_id)
    )
    documents = docs_result.scalars().all()

    return {
        "collection_id": collection_id,
        "documents": [d.to_dict() for d in documents],
    }


@router.delete("/{collection_id}/documents/{document_id}")
async def remove_document_from_collection(
    collection_id: int,
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Remove a document from a collection."""
    result = await db.execute(
        select(CollectionDocument).where(
            CollectionDocument.collection_id == collection_id,
            CollectionDocument.document_id == document_id,
        )
    )
    cd = result.scalar_one_or_none()

    if not cd:
        raise HTTPException(status_code=404, detail="Document not in collection")

    await db.delete(cd)
    await db.commit()

    return {"status": "removed", "collection_id": collection_id, "document_id": document_id}
