# Docling API

Document processing API powered by [Docling](https://docling-project.github.io/docling).

## Features

- **Multi-format support**: PDF, DOCX, PPTX, XLSX, HTML, images, and more
- **Multiple output formats**: Markdown, plain text, JSON
- **Streaming support**: Regular streaming, per-page streaming, and SSE
- **Bulk processing**: Process multiple documents concurrently
- **Image extraction**: Extract embedded images and page renders

## Installation

```bash
uv sync
```

## Usage

Start the server:

```bash
uv run uvicorn main:app --reload
```

API documentation available at: http://localhost:8000/docs

## API Endpoints

### Documents

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/documents/process` | POST | Convert a document to specified format |
| `/documents/process/stream` | POST | Stream converted content |
| `/documents/process/stream/pages` | POST | Stream content page by page (NDJSON) |
| `/documents/process/sse` | POST | Stream with Server-Sent Events |
| `/documents/process/bulk` | POST | Process multiple documents |

### Images

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/images/extract` | POST | Extract images from a document |

### Health

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/live` | GET | Liveness probe |
| `/health/ready` | GET | Readiness probe |

## Project Structure

```
api-docs-1/
├── main.py                    # FastAPI app entry point
├── api/
│   └── routes/
│       ├── documents.py       # Document processing endpoints
│       ├── images.py          # Image extraction endpoint
│       └── health.py          # Health check endpoints
├── core/
│   ├── config.py              # Configuration settings
│   ├── schemas.py             # Pydantic response models
│   └── error_handlers.py      # Centralized error handling
└── services/
    ├── file_utils.py          # File handling utilities
    ├── docling_converter.py   # Document conversion logic
    ├── docling_streaming.py   # Streaming utilities
    ├── docling_service.py     # High-level orchestration
    └── image_service.py       # Image extraction service
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload file size in MB |
| `DOCLING_OCR_BACKEND` | `tesseract` | OCR backend |
| `DOCLING_OCR_LANGS` | `eng` | OCR languages |

## License

MIT
