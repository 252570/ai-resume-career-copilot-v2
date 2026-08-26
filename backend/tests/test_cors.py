from fastapi.testclient import TestClient

from app.main import app


def test_local_frontend_preflight_allows_authenticated_application_updates() -> None:
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/applications/00000000-0000-0000-0000-000000000000",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "PATCH",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
    assert response.status_code == 200
    assert "PATCH" in response.headers["access-control-allow-methods"]
    assert "DELETE" in response.headers["access-control-allow-methods"]
    assert "authorization" in response.headers["access-control-allow-headers"].lower()
    assert response.headers["access-control-allow-credentials"] == "true"
