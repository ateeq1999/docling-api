"""Application configuration."""

import os
import secrets

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# OCR Configuration
OCR_ENABLED = os.getenv("DOCLING_OCR_ENABLED", "true").lower() == "true"
OCR_LANGUAGES = os.getenv("DOCLING_OCR_LANGS", "en").split(",")

# Performance
NUM_THREADS = int(os.getenv("OMP_NUM_THREADS", "4"))

# Authentication
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Auth settings
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"
