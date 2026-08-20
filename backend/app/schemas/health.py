"""Typed health endpoint response model."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Stable liveness response returned by the API."""

    status: str = Field(description="Current service status.")
    service: str = Field(description="Stable service identifier.")
    version: str = Field(description="API implementation version.")
