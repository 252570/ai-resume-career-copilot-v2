"""Typed health endpoint response models."""

from typing import Literal

from pydantic import BaseModel, Field

DatabaseState = Literal["connected", "unconfigured", "unreachable"]


class HealthResponse(BaseModel):
    """Liveness response returned by the API.

    The `database` field exists because a bare liveness check is actively
    misleading in deployment: this process starts and answers requests happily
    with no database configured, so a plain `{"status": "ok"}` reported healthy
    while every data-backed endpoint returned 500. Liveness still returns 200
    regardless of database state, so a transient database fault does not cause
    the platform to restart a perfectly good process. Use `/health/ready` when
    the caller needs to know whether the service can actually serve traffic.
    """

    status: str = Field(description="Current service status.")
    service: str = Field(description="Stable service identifier.")
    version: str = Field(description="API implementation version.")
    database: DatabaseState = Field(
        description=(
            "Database availability: 'connected' when a test query succeeds, "
            "'unconfigured' when DATABASE_URL is absent or not PostgreSQL, "
            "'unreachable' when configured but the connection or query failed."
        )
    )


class ReadinessResponse(BaseModel):
    """Readiness response reporting whether dependencies are actually usable."""

    ready: bool = Field(description="True only when every checked dependency is usable.")
    database: DatabaseState = Field(description="Database availability, as in HealthResponse.")
    detail: str = Field(description="Human-readable explanation of the current readiness state.")
