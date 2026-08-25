"""System health contract for deployment and smoke-test verification."""

from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import DatabaseConfigurationError
from app.db.session import get_engine
from app.schemas.health import DatabaseState, HealthResponse, ReadinessResponse

router = APIRouter()

SERVICE_NAME = "career-copilot-api"
SERVICE_VERSION = "0.1.0"

_DATABASE_DETAIL = {
    "connected": "All checked dependencies are usable.",
    "unconfigured": (
        "DATABASE_URL is not set to a PostgreSQL connection string. Data-backed endpoints "
        "will fail until it is configured in the runtime environment."
    ),
    "unreachable": (
        "DATABASE_URL is configured but the database did not answer. Check that the host is "
        "reachable, the credentials are valid, and migrations have been applied."
    ),
}


def _probe_database() -> DatabaseState:
    """Classify database availability without leaking connection details.

    Distinguishing 'unconfigured' from 'unreachable' is the point of this function.
    Both previously surfaced as an identical opaque 500, which made a missing
    environment variable indistinguishable from a down database and turned a
    one-line fix into a guessing game.
    """
    try:
        engine = get_engine()
    except DatabaseConfigurationError:
        return "unconfigured"
    except SQLAlchemyError:
        # A URL that passes the scheme check but cannot build an engine at all
        # (bad driver, unparseable host) is a configuration fault, not an outage.
        return "unconfigured"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return "unreachable"
    return "connected"


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def read_health() -> HealthResponse:
    """Report liveness, always 200, annotated with observed database state."""
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        database=_probe_database(),
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessResponse}},
)
def read_readiness(response: Response) -> ReadinessResponse:
    """Return 200 only when dependencies are usable, otherwise 503.

    Kept separate from liveness on purpose: a platform health check pointed at a
    database-dependent endpoint restarts a healthy process during a database
    blip, which turns a recoverable fault into an outage.
    """
    database = _probe_database()
    ready = database == "connected"
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(ready=ready, database=database, detail=_DATABASE_DETAIL[database])
