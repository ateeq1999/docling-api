"""Docling document conversion utilities."""

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.exceptions import ConversionError

from core.config import OCR_ENABLED, OCR_LANGUAGES

logger = logging.getLogger("docling_api")


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


def create_converter() -> DocumentConverter:
    """Create a configured DocumentConverter instance."""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = OCR_ENABLED
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    if OCR_ENABLED:
        pipeline_options.ocr_options.lang = OCR_LANGUAGES

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )


def convert_file(path: Path, output_format: OutputFormat) -> str:
    """
    Convert a document file to the specified output format.
    
    Raises:
        ConversionError: If the document cannot be converted.
        ValueError: If the output format is not supported.
    """
    converter = create_converter()

    try:
        logger.info("Converting document: %s", path.name)
        result = converter.convert(str(path))
    except ConversionError as e:
        logger.error("Conversion failed: %s", e)
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
    converter = create_converter()

    try:
        logger.info("Loading document: %s", path.name)
        result = converter.convert(str(path))
    except ConversionError as e:
        logger.error("Document load failed: %s", e)
        raise ConversionError(f"Invalid or unsupported document: {e}") from e

    return result.document
