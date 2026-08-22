from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.v1.routes.resumes import get_resume_storage
from app.db.session import get_db_session
from app.main import app
from app.services.resume_parser import TEXT_CONTENT_TYPE
from app.services.resume_storage import ResumeStorage


def test_generates_persisted_roadmap_and_projects(db_session: Session, tmp_path) -> None:
    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    app.dependency_overrides[get_resume_storage] = lambda: ResumeStorage(tmp_path / "resumes")
    with TestClient(app) as client:
        resume = client.post("/api/v1/resumes/upload", files={"file": ("resume.txt", b"Avery Example\nSkills\nPython", TEXT_CONTENT_TYPE)}).json()
        job = client.post("/api/v1/jobs", json={"description": "Platform Engineer\nRequirements\nPython, PostgreSQL, Docker"}).json()
        analysis = client.post("/api/v1/analyses/match", json={"resume_id": resume["id"], "job_id": job["id"]}).json()
        response = client.post(f"/api/v1/plans/{analysis['id']}/generate")
        assert response.status_code == 201, response.text
        payload = response.json()
        assert {item["skill"] for item in payload["roadmap"]} == {"PostgreSQL", "Docker"}
        assert {project["title"] for project in payload["projects"]} == {"PostgreSQL Evidence Project", "Docker Evidence Project"}
        assert client.get(f"/api/v1/plans/{analysis['id']}").json() == payload
    app.dependency_overrides.clear()
