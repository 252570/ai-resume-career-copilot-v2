"""Contract tests for the public Phase 1 health endpoint."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_service_contract() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "career-copilot-api",
        "version": "0.1.0",
    }
