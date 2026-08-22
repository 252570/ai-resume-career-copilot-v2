from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db_session
from app.main import app
from app.api.v1.routes.resumes import get_resume_storage
from app.services.resume_parser import TEXT_CONTENT_TYPE
from app.services.resume_storage import ResumeStorage


def test_signup_login_and_me(db_session: Session, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-only-signing-secret-with-sufficient-length")
    get_settings.cache_clear()

    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/signup", json={"email": "user@example.com", "display_name": "Example User", "password": "correct-horse-battery-staple"})
        assert response.status_code == 201, response.text
        payload = response.json()
        assert payload["token_type"] == "bearer"
        assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"}).json()["email"] == "user@example.com"
        assert client.post("/api/v1/auth/signup", json={"email": "user@example.com", "display_name": "Second User", "password": "correct-horse-battery-staple"}).status_code == 409
        assert client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "incorrect-password"}).status_code == 401
        login = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "correct-horse-battery-staple"})
        assert login.status_code == 200
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_authenticated_users_cannot_access_another_users_resume(db_session: Session, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-only-signing-secret-with-sufficient-length")
    get_settings.cache_clear()

    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    app.dependency_overrides[get_resume_storage] = lambda: ResumeStorage(tmp_path / "resumes")
    with TestClient(app) as client:
        first = client.post("/api/v1/auth/signup", json={"email": "one@example.com", "display_name": "First User", "password": "correct-horse-battery-staple"}).json()
        second = client.post("/api/v1/auth/signup", json={"email": "two@example.com", "display_name": "Second User", "password": "correct-horse-battery-staple"}).json()
        first_headers = {"Authorization": f"Bearer {first['access_token']}"}
        second_headers = {"Authorization": f"Bearer {second['access_token']}"}
        resume = client.post("/api/v1/resumes/upload", files={"file": ("private.txt", b"Private Candidate\nSkills\nPython", TEXT_CONTENT_TYPE)}, headers=first_headers).json()
        assert client.get("/api/v1/resumes", headers=second_headers).json() == []
        assert client.get(f"/api/v1/resumes/{resume['id']}", headers=second_headers).status_code == 404
    app.dependency_overrides.clear()
    get_settings.cache_clear()
