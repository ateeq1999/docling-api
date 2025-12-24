"""Health check endpoints."""

from fastapi import APIRouter

from core.schemas import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/live", response_model=HealthResponse)
async def liveness():
    """Liveness probe - indicates the service is running."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
async def readiness():
    """Readiness probe - indicates the service is ready to accept requests."""
    return HealthResponse(status="ok")
