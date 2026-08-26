from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.v1.routes.resumes import get_resume_storage
from app.core.config import get_settings
from app.db.session import get_db_session
from app.main import app
from app.services.resume_parser import TEXT_CONTENT_TYPE
from app.services.resume_storage import ResumeStorage


def test_authenticated_user_can_review_resume_evidence(db_session: Session, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-only-signing-secret-with-sufficient-length")
    get_settings.cache_clear()

    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    app.dependency_overrides[get_resume_storage] = lambda: ResumeStorage(tmp_path / "resumes")
    with TestClient(app) as client:
        account = client.post("/api/v1/auth/signup", json={"email": "review@example.com", "display_name": "Review User", "password": "correct-horse-battery-staple"}).json()
        headers = {"Authorization": f"Bearer {account['access_token']}"}
        uploaded = client.post("/api/v1/resumes/upload", headers=headers, files={"file": ("resume.txt", b"Avery Example\nSkills\nPython", TEXT_CONTENT_TYPE)}).json()
        corrected = client.patch(
            f"/api/v1/resumes/{uploaded['id']}",
            headers=headers,
            json={
                "candidate_name": "Avery Example",
                "email": "avery@example.com",
                "phone": None,
                "linkedin": None,
                "github": None,
                "summary": ["Backend engineer"],
                "skills": ["Python", "Postgres"],
                "education": ["BSc Computer Science"],
                "experience": ["Built APIs"],
                "projects": [],
                "certifications": [],
                "links": [],
            },
        )
        assert corrected.status_code == 200, corrected.text
        assert corrected.json()["status"] == "reviewed"
        assert corrected.json()["parsed"]["skills"] == ["Python", "Postgres"]
    app.dependency_overrides.clear()
    get_settings.cache_clear()
