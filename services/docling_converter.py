"""Docling document conversion utilities."""

import json
from enum import Enum
from pathlib import Path
from typing import Any

from docling.document_converter import DocumentConverter
from docling.exceptions import ConversionError


class OutputFormat(str, Enum):
    """Supported output formats for document conversion."""

    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"


MEDIA_TYPES = {
    OutputFormat.TEXT: "text/plain",
    OutputFormat.MARKDOWN: "text/plain",
    OutputFormat.JSON: "application/json",
}


def get_media_type(output_format: OutputFormat) -> str:
    """Get the HTTP media type for an output format."""
    return MEDIA_TYPES.get(output_format, "text/plain")


def convert_file(path: Path, output_format: OutputFormat) -> str:
    """
    Convert a document file to the specified output format.
    
    Raises:
        ConversionError: If the document cannot be converted.
        ValueError: If the output format is not supported.
    """
    converter = DocumentConverter()

    try:
        result = converter.convert(str(path))
    except ConversionError as e:
        raise ConversionError(f"Invalid or unsupported document: {e}") from e

    doc = result.document

    if output_format is OutputFormat.TEXT:
        return doc.export_to_text()

    if output_format is OutputFormat.MARKDOWN:
        return doc.export_to_markdown()

    if output_format is OutputFormat.JSON:
        data = doc.export_to_dict()
        return json.dumps(data)

    raise ValueError(f"Unsupported format: {output_format}")


def load_document_from_path(path: Path) -> Any:
    """
    Load a document from a file path and return the DoclingDocument.
    
    Raises:
        ConversionError: If the document cannot be converted.
    """
    converter = DocumentConverter()

    try:
        result = converter.convert(str(path))
    except ConversionError as e:
        raise ConversionError(f"Invalid or unsupported document: {e}") from e

    return result.document
