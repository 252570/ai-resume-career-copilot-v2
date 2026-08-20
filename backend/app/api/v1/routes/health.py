"""System health contract for deployment and smoke-test verification."""

from fastapi import APIRouter, status

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def read_health() -> HealthResponse:
    """Return the minimal Phase 1 liveness response."""
    return HealthResponse(status="ok", service="career-copilot-api", version="0.1.0")
