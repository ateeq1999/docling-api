"""Pydantic schemas for API responses."""

from typing import Literal

from pydantic import BaseModel


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
