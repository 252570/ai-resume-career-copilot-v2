from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.v1.routes.resumes import get_resume_storage
from app.db.session import get_db_session
from app.main import app
from app.services.resume_parser import TEXT_CONTENT_TYPE
from app.services.resume_storage import ResumeStorage


def _client(db_session: Session, tmp_path) -> TestClient:
    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    app.dependency_overrides[get_resume_storage] = lambda: ResumeStorage(tmp_path / "resumes")
    return TestClient(app)


def test_creates_explainable_deterministic_match(db_session: Session, tmp_path) -> None:
    with _client(db_session, tmp_path) as client:
        resume = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("resume.txt", b"Avery Example\nSkills\nPython, FastAPI\nExperience\nAPI engineer", TEXT_CONTENT_TYPE)},
        ).json()
        job = client.post(
            "/api/v1/jobs",
            json={"description": "Backend Engineer\nRequirements\nPython, FastAPI, PostgreSQL\nPreferred Qualifications\nDocker"},
        ).json()
        analysis = client.post("/api/v1/analyses/match", json={"resume_id": resume["id"], "job_id": job["id"]})
        assert analysis.status_code == 201, analysis.text
        payload = analysis.json()
        assert payload["match_score"] > 0
        assert {"Python", "FastAPI"}.issubset(payload["matched_skills"])
        assert "PostgreSQL" in payload["missing_skills"]
        assert any(gap["skill"] == "PostgreSQL" and gap["priority"] == "critical" for gap in payload["skill_gaps"])
        assert payload["ats"]["keyword_coverage"] < 100
        assert payload["resume_evidence"]["Python"]
        repeat = client.post("/api/v1/analyses/match", json={"resume_id": resume["id"], "job_id": job["id"]})
        assert repeat.status_code == 201
        assert repeat.json()["id"] == payload["id"]
    app.dependency_overrides.clear()
