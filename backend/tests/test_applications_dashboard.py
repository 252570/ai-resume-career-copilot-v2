from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db_session
from app.main import app


def test_application_tracker_and_dashboard_are_user_scoped(db_session: Session, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-only-signing-secret-with-sufficient-length")
    get_settings.cache_clear()

    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    with TestClient(app) as client:
        owner = client.post("/api/v1/auth/signup", json={"email": "tracker@example.com", "display_name": "Tracker", "password": "correct-horse-battery-staple"}).json()
        other = client.post("/api/v1/auth/signup", json={"email": "viewer@example.com", "display_name": "Viewer", "password": "correct-horse-battery-staple"}).json()
        headers = {"Authorization": f"Bearer {owner['access_token']}"}
        created = client.post("/api/v1/applications", headers=headers, json={"company_name": "Acme", "role_title": "Backend Engineer", "status": "applied", "notes": "Submitted through company site."})
        assert created.status_code == 201, created.text
        application = created.json()
        assert application["applied_at"] is not None
        updated = client.patch(f"/api/v1/applications/{application['id']}", headers=headers, json={"status": "screening"})
        assert updated.status_code == 200
        dashboard = client.get("/api/v1/dashboard", headers=headers).json()
        assert dashboard["application_count"] == 1
        assert dashboard["applications_by_status"] == {"screening": 1}
        assert client.get("/api/v1/applications", headers={"Authorization": f"Bearer {other['access_token']}"}).json() == []
    app.dependency_overrides.clear()
    get_settings.cache_clear()
