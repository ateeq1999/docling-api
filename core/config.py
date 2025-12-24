"""Application configuration."""

import os

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# OCR Configuration
OCR_ENABLED = os.getenv("DOCLING_OCR_ENABLED", "true").lower() == "true"
OCR_LANGUAGES = os.getenv("DOCLING_OCR_LANGS", "en").split(",")

# Performance
NUM_THREADS = int(os.getenv("OMP_NUM_THREADS", "4"))
