import os

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Docling-supported configuration
os.environ.setdefault("DOCLING_OCR_BACKEND", "tesseract")
os.environ.setdefault("DOCLING_OCR_LANGS", "eng")
os.environ.setdefault("DOCLING_LAYOUT_BACKEND", "default")
