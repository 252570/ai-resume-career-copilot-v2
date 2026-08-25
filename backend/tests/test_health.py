"""Contract tests for the health endpoints and the database-fault error contract.

These tests exist because a deployed instance reported {"status": "ok"} from /health
while every data endpoint returned a bare 500. Two defects produced that: the health
check never touched the database, and DatabaseConfigurationError had no handler, so a
missing environment variable was indistinguishable from an application crash.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes import health as health_routes
from app.core.config import get_settings
from app.db.session import get_engine, get_session_factory
from app.main import app

SERVICE_CONTRACT = {"status": "ok", "service": "career-copilot-api", "version": "0.1.0"}
DATABASE_STATES = ("connected", "unconfigured", "unreachable")


@pytest.fixture
def unconfigured_database(monkeypatch: pytest.MonkeyPatch, tmp_path) -> Generator[None, None, None]:
    """Present the process with no database configuration at all.

    chdir matters as much as delenv: Settings declares env_file=".env" relative to the
    working directory, so deleting the variable alone still lets pydantic-settings read
    backend/.env off a developer machine and quietly pass a test that would fail in
    deployment. Caches are cleared on both sides so neither a real nor a fake engine
    leaks between tests.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    for cache in (get_settings, get_engine, get_session_factory):
        cache.cache_clear()
    yield
    for cache in (get_settings, get_engine, get_session_factory):
        cache.cache_clear()


def test_health_reports_liveness_and_observed_database_state() -> None:
    """Liveness keeps its original contract and gains a database field."""
    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert {key: payload[key] for key in SERVICE_CONTRACT} == SERVICE_CONTRACT
    assert payload["database"] in DATABASE_STATES


@pytest.mark.parametrize("state", DATABASE_STATES)
def test_health_stays_200_for_every_database_state(monkeypatch: pytest.MonkeyPatch, state: str) -> None:
    """A database fault must not fail liveness.

    Render restarts a service whose health check fails, so returning non-200 here would
    escalate a recoverable database blip into a crash loop while reporting the fault.
    """
    monkeypatch.setattr(health_routes, "_probe_database", lambda: state)

    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["database"] == state


def test_readiness_is_200_only_when_the_database_is_usable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(health_routes, "_probe_database", lambda: "connected")

    response = TestClient(app).get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "ready": True,
        "database": "connected",
        "detail": "All checked dependencies are usable.",
    }


@pytest.mark.parametrize("state", ["unconfigured", "unreachable"])
def test_readiness_returns_503_and_names_the_fault(monkeypatch: pytest.MonkeyPatch, state: str) -> None:
    monkeypatch.setattr(health_routes, "_probe_database", lambda: state)

    response = TestClient(app).get("/api/v1/health/ready")

    assert response.status_code == 503
    payload = response.json()
    assert payload["ready"] is False
    assert payload["database"] == state
    assert payload["detail"] == health_routes._DATABASE_DETAIL[state]


def test_health_detects_missing_database_configuration(unconfigured_database: None) -> None:
    """The real probe, not a stub, must classify an unset DATABASE_URL correctly."""
    client = TestClient(app)

    assert client.get("/api/v1/health").json()["database"] == "unconfigured"

    readiness = client.get("/api/v1/health/ready")
    assert readiness.status_code == 503
    assert readiness.json()["database"] == "unconfigured"


def test_database_dependent_endpoint_returns_503_with_a_body(unconfigured_database: None) -> None:
    """The regression this fixes: a config fault must not surface as a bare 500.

    The session is a route dependency, so it fails before request validation. That is
    why a well-formed request and a malformed one both returned 500 previously, hiding
    the fact that nothing was wrong with the request at all.
    """
    response = TestClient(app).post(
        "/api/v1/auth/signup",
        json={"email": "user@example.com", "display_name": "Example User", "password": "correct-horse-battery-staple"},
    )

    assert response.status_code == 503
    payload = response.json()
    assert "DATABASE_URL" in payload["detail"]
    assert "/api/v1/health/ready" in payload["hint"]


def test_configuration_fault_is_not_reported_as_a_client_error(unconfigured_database: None) -> None:
    """An invalid body must still yield 503, proving the fault is server-side.

    A 422 here would tell the caller to fix their request when the request was never
    the problem.
    """
    response = TestClient(app).post("/api/v1/auth/signup", json={"not": "a signup payload"})

    assert response.status_code == 503
