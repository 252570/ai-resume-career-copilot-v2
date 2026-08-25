"""FastAPI application entry point for the Phase 1 foundation."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import DatabaseConfigurationError


def create_application() -> FastAPI:
    """Create the API with explicit metadata and versioned routing."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Phase 3 service: secure resume upload, deterministic parsing, and metadata retrieval.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # DatabaseConfigurationError subclasses RuntimeError, so without this handler it
    # escaped as a bare "Internal Server Error" with no body. Because the database
    # session is a route dependency, that 500 was raised before request validation,
    # so even a malformed request body returned 500 instead of 422 -- which made a
    # missing environment variable look like a total application failure. 503 is the
    # correct status: the service is reachable but a dependency is not usable, and the
    # condition is fixed by configuration rather than by changing the request.
    @application.exception_handler(DatabaseConfigurationError)
    async def handle_database_configuration_error(_: Request, exc: DatabaseConfigurationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": str(exc),
                "hint": "Check the service environment configuration, then query /api/v1/health/ready.",
            },
        )

    # Connection failures are equally not the caller's fault. The message is
    # deliberately fixed text: SQLAlchemy's own message can embed the host, port,
    # and username from the connection URL, which must never reach a client.
    @application.exception_handler(OperationalError)
    async def handle_database_operational_error(_: Request, __: OperationalError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "The database is currently unavailable. Please retry shortly.",
                "hint": "Query /api/v1/health/ready to confirm dependency status.",
            },
        )

    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
