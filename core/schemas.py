"""Pydantic schemas for API responses."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BulkDocumentResult(BaseModel):
    """Result for a single document in bulk processing."""

    filename: str | None
    status: Literal["success", "error"]
    content: str | None = None
    error: str | None = None


class ImageInfo(BaseModel):
    """Information about an extracted image."""

    type: Literal["embedded", "page_render"]
    page: int
    index: int | None = None
    width: int
    height: int
    bbox: list[float] | None = None
    path: str


class ImagesResponse(BaseModel):
    """Response for image extraction endpoint."""

    count: int
    images: list[ImageInfo]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


class RootResponse(BaseModel):
    """Root endpoint response."""

    name: str
    version: str
    docs: str


# Chunk schemas
class ChunkResponse(BaseModel):
    """Response for a single chunk."""

    id: int
    document_id: int
    content: str
    context: str
    chunk_index: int
    page_number: int | None
    section_title: str | None
    token_count: int
    metadata: dict
    has_embedding: bool
    created_at: datetime | None


class ChunksResponse(BaseModel):
    """Response for listing chunks."""

    count: int
    chunks: list[ChunkResponse]


# Search schemas
class SearchRequest(BaseModel):
    """Request for semantic search."""

    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    document_ids: list[int] | None = None
    file_types: list[str] | None = None


class SearchResultItem(BaseModel):
    """A single search result."""

    chunk_id: int
    document_id: int
    filename: str
    content: str
    score: float
    page_number: int | None
    section_title: str | None


class SearchResponse(BaseModel):
    """Response for semantic search."""

    query: str
    results: list[SearchResultItem]


# RAG/Chat schemas
class RAGRequest(BaseModel):
    """Request for RAG query."""

    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[int] | None = None
    llm_provider: Literal["openai", "ollama"] = "openai"
    llm_model: str | None = None
    stream: bool = False


class SourceInfo(BaseModel):
    """Source information for RAG response."""

    chunk_id: int
    document_id: int
    filename: str
    content: str
    score: float
    page_number: int | None


class RAGResponseSchema(BaseModel):
    """Response for RAG query."""

    answer: str
    sources: list[SourceInfo]


# Chat session schemas
class CreateSessionRequest(BaseModel):
    """Request to create a chat session."""

    title: str | None = None
    document_ids: list[int] | None = None


class ChatSessionResponse(BaseModel):
    """Response for a chat session."""

    id: int
    title: str | None
    document_ids: list[int]
    created_at: datetime | None


class SendMessageRequest(BaseModel):
    """Request to send a message in a chat session."""

    content: str
    llm_provider: Literal["openai", "ollama"] = "openai"
    llm_model: str | None = None
    stream: bool = False


class ChatMessageResponse(BaseModel):
    """Response for a chat message."""

    id: int
    session_id: int
    role: str
    content: str
    sources: list[SourceInfo]
    created_at: datetime | None


class ChatHistoryResponse(BaseModel):
    """Response for chat history."""

    session: ChatSessionResponse
    messages: list[ChatMessageResponse]


# Process with chunking
class ProcessWithChunkingResponse(BaseModel):
    """Response for document processing with chunking."""

    document_id: int
    filename: str
    chunk_count: int
    status: str
