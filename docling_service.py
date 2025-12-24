# docling_service.py
from typing import Dict, Any
from pathlib import Path
import json

# Assuming ConverterConfig and DocumentConverter are from a docling library
# The actual imports might look different based on the library
# If these imports are not resolved, further context will be needed from the user.
from docling.document_converter import ConverterConfig, DocumentConverter


def process_document(file_path: Path, output_format: str) -> Any:
    """
    Processes a document using docling and returns the output in the desired format.
    """
    config = ConverterConfig(ocr_backend="default", layout_backend="default")
    converter = DocumentConverter(config=config)

    result = converter.convert(str(file_path))

    if output_format == "text":
        return result.document.export_to_text()
    elif output_format == "markdown":
        return result.document.export_to_markdown()
    elif output_format == "json":
        # Docling's export_to_json might return a string or dict.
        # Ensure it's a dict for consistent JSON response.
        json_output = result.document.export_to_json()
        if isinstance(json_output, str):
            return json.loads(json_output)
        return json_output
    else:
        raise ValueError(f"Unsupported output format: {output_format}")