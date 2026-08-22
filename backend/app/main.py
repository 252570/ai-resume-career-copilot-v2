"""FastAPI application entry point for the Phase 1 foundation."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings


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
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
