"""Docling API - Document processing service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from api.routes import router
from core.database import init_db
from core.error_handlers import init_error_handlers
from core.schemas import RootResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger("docling_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(
    title="Docling API",
    description="Document processing API powered by Docling",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1024)

init_error_handlers(app)

app.include_router(router)


@app.get("/", response_model=RootResponse)
async def root():
    """API root endpoint with metadata."""
    return RootResponse(
        name="Docling API",
        version="0.1.0",
        docs="/docs",
    )
