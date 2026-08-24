from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db_session
from app.main import app


def test_interview_practice_generates_questions_and_feedback(db_session: Session, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-only-signing-secret-with-sufficient-length")
    get_settings.cache_clear()

    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session
    with TestClient(app) as client:
        owner = client.post("/api/v1/auth/signup", json={"email": "candidate@example.com", "display_name": "Candidate", "password": "correct-horse-battery-staple"}).json()
        other = client.post("/api/v1/auth/signup", json={"email": "other@example.com", "display_name": "Other", "password": "correct-horse-battery-staple"}).json()
        headers = {"Authorization": f"Bearer {owner['access_token']}"}
        job = client.post("/api/v1/jobs", headers=headers, json={"description": "Backend Engineer\nRequirements\nPython, FastAPI"}).json()
        created = client.post("/api/v1/interviews", headers=headers, json={"job_id": job["id"], "question_count": 3})
        assert created.status_code == 201, created.text
        session_data = created.json()
        assert len(session_data["questions"]) == 3
        answer = "Situation: our API was slow. My task was to improve it. I used Python and FastAPI to profile endpoints, optimize queries, and add tests. As a result, response time fell by 35% for 10,000 daily requests while the team gained a clear deployment checklist."
        responded = client.post(f"/api/v1/interviews/{session_data['id']}/responses", headers=headers, json={"question_index": 1, "answer": answer})
        assert responded.status_code == 200, responded.text
        feedback = responded.json()["responses"][0]["feedback"]
        assert feedback["score"] > 0
        assert "deterministic structure feedback" in feedback["disclaimer"]
        assert client.get(f"/api/v1/interviews/{session_data['id']}", headers={"Authorization": f"Bearer {other['access_token']}"}).status_code == 404
    app.dependency_overrides.clear()
    get_settings.cache_clear()
