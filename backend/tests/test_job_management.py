from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.main import app
from app.services.resume_parser import TEXT_CONTENT_TYPE


def _client(db_session: Session) -> TestClient:
    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    return TestClient(app)


def test_creates_parses_and_lists_job_descriptions(db_session: Session) -> None:
    with _client(db_session) as client:
        response = client.post(
            "/api/v1/jobs",
            json={
                "title": "Backend Engineer",
                "company_name": "Example Labs",
                "description": """Backend Engineer
Requirements:
Python, FastAPI, PostgreSQL, Docker
3+ years building production APIs.
Bachelor's degree in Computer Science or equivalent experience.
Preferred Qualifications:
AWS, Machine Learning
""",
            },
        )
        assert response.status_code == 201, response.text
        payload = response.json()
        assert payload["title"] == "Backend Engineer"
        assert payload["company_name"] == "Example Labs"
        assert {"Python", "FastAPI", "PostgreSQL", "Docker"}.issubset(payload["parsed"]["required_skills"])
        assert {"AWS", "Machine Learning"}.issubset(payload["parsed"]["preferred_skills"])
        assert payload["parsed"]["experience_requirements"]
        assert payload["parsed"]["education_requirements"]
        job_id = payload["id"]
        assert client.get(f"/api/v1/jobs/{job_id}").json()["id"] == job_id
        assert len(client.get("/api/v1/jobs").json()) == 1
    app.dependency_overrides.clear()


def test_uploads_text_job_description(db_session: Session) -> None:
    with _client(db_session) as client:
        response = client.post(
            "/api/v1/jobs/upload",
            files={"file": ("job.txt", b"Data Engineer\nRequirements\nPython, SQL, Docker", TEXT_CONTENT_TYPE)},
        )
        assert response.status_code == 201, response.text
        assert response.json()["title"] == "job"
        assert {"Python", "SQL", "Docker"}.issubset(response.json()["parsed"]["required_skills"])
    app.dependency_overrides.clear()


def test_rejects_duplicate_job_for_same_authenticated_account(db_session: Session, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-only-signing-secret-with-sufficient-length")
    from app.core.config import get_settings

    get_settings.cache_clear()
    with _client(db_session) as client:
        account = client.post("/api/v1/auth/signup", json={"email": "jobs@example.com", "display_name": "Jobs User", "password": "correct-horse-battery-staple"}).json()
        headers = {"Authorization": f"Bearer {account['access_token']}"}
        payload = {"title": "Backend Engineer", "company_name": "Example Labs", "description": "Python FastAPI PostgreSQL Docker production backend requirements."}
        assert client.post("/api/v1/jobs", headers=headers, json=payload).status_code == 201
        duplicate = client.post("/api/v1/jobs", headers=headers, json=payload)
        assert duplicate.status_code == 409
        assert "already saved" in duplicate.json()["detail"]
    app.dependency_overrides.clear()
    get_settings.cache_clear()
