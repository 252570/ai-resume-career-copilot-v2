"""Compose Phase 1 versioned API routers."""

from fastapi import APIRouter

from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.account import router as account_router
from app.api.v1.routes.analyses import router as analyses_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.applications import router as applications_router
from app.api.v1.routes.dashboard import router as dashboard_router
from app.api.v1.routes.interviews import router as interviews_router
from app.api.v1.routes.jobs import router as jobs_router
from app.api.v1.routes.plans import router as plans_router
from app.api.v1.routes.resumes import router as resumes_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["system"])
api_router.include_router(account_router, tags=["account"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(applications_router, tags=["applications"])
api_router.include_router(dashboard_router, tags=["dashboard"])
api_router.include_router(analyses_router, tags=["analyses"])
api_router.include_router(resumes_router, tags=["resumes"])
api_router.include_router(jobs_router, tags=["jobs"])
api_router.include_router(interviews_router, tags=["interviews"])
api_router.include_router(plans_router, tags=["plans"])
