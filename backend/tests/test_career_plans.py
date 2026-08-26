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


def test_roadmap_completion_persists_for_authenticated_owner(db_session: Session, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-only-signing-secret-with-sufficient-length")
    from app.core.config import get_settings

    get_settings.cache_clear()

    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    app.dependency_overrides[get_resume_storage] = lambda: ResumeStorage(tmp_path / "resumes")
    with TestClient(app) as client:
        account = client.post("/api/v1/auth/signup", json={"email": "roadmap@example.com", "display_name": "Roadmap User", "password": "correct-horse-battery-staple"}).json()
        headers = {"Authorization": f"Bearer {account['access_token']}"}
        resume = client.post("/api/v1/resumes/upload", headers=headers, files={"file": ("resume.txt", b"Avery Example\nSkills\nPython", TEXT_CONTENT_TYPE)}).json()
        job = client.post("/api/v1/jobs", headers=headers, json={"description": "Platform Engineer\nRequirements\nPython, PostgreSQL, Docker"}).json()
        analysis = client.post("/api/v1/analyses/match", headers=headers, json={"resume_id": resume["id"], "job_id": job["id"]}).json()
        plan = client.post(f"/api/v1/plans/{analysis['id']}/generate", headers=headers).json()
        item_id = plan["roadmap"][0]["id"]
        updated = client.patch(f"/api/v1/plans/items/{item_id}", headers=headers, json={"completed": True})
        assert updated.status_code == 200, updated.text
        assert next(item for item in updated.json()["roadmap"] if item["id"] == item_id)["completed"] is True
        persisted = client.get(f"/api/v1/plans/{analysis['id']}", headers=headers).json()
        assert next(item for item in persisted["roadmap"] if item["id"] == item_id)["completed"] is True
    app.dependency_overrides.clear()
    get_settings.cache_clear()
