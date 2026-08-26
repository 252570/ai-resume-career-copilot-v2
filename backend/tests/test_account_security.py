from __future__ import annotations

from fastapi import HTTPException, Request

from app.api.v1.routes.account import delete_account, export_account
from app.models import Job, Resume, User
from app.security import rate_limit


def _request(ip: str = "203.0.113.20") -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/auth/login",
            "headers": [],
            "client": (ip, 443),
            "server": ("testserver", 443),
            "scheme": "https",
        }
    )


def test_auth_rate_limit_returns_retry_after_header() -> None:
    rate_limit._attempts.clear()
    request = _request()
    for _ in range(rate_limit._MAX_ATTEMPTS_PER_WINDOW):
        rate_limit.enforce_auth_rate_limit(request, "person@example.com")

    try:
        rate_limit.enforce_auth_rate_limit(request, "person@example.com")
    except HTTPException as exc:
        assert exc.status_code == 429
        assert exc.headers == {"Retry-After": exc.headers["Retry-After"]}
        assert int(exc.headers["Retry-After"]) > 0
    else:
        raise AssertionError("The authentication limiter did not reject the next attempt")
    rate_limit._attempts.clear()


def test_account_export_is_owner_scoped(db_session) -> None:
    user = User(email="export@example.com", display_name="Export User", password_hash="hash")
    other_user = User(email="other@example.com", display_name="Other User", password_hash="hash")
    db_session.add_all([user, other_user])
    db_session.flush()
    db_session.add_all(
        [
            Resume(user_id=user.id, title="Resume", original_filename="resume.txt", parsed_data={"skills": ["Python"]}),
            Resume(user_id=other_user.id, title="Other Resume", original_filename="other.txt", parsed_data={"skills": ["Ruby"]}),
            Job(user_id=user.id, title="Backend Engineer", description="Python and PostgreSQL role requirements."),
            Job(user_id=other_user.id, title="Other Role", description="Ruby role requirements."),
        ]
    )
    db_session.commit()

    exported = export_account(user=user, session=db_session)

    assert exported["profile"]["email"] == "export@example.com"
    assert [item["title"] for item in exported["resumes"]] == ["Resume"]
    assert [item["title"] for item in exported["jobs"]] == ["Backend Engineer"]


def test_delete_account_removes_user_owned_records(db_session) -> None:
    user = User(email="delete@example.com", display_name="Delete User", password_hash="hash")
    db_session.add(user)
    db_session.flush()
    db_session.add(Resume(user_id=user.id, title="Resume", original_filename="resume.txt"))
    db_session.add(Job(user_id=user.id, title="Role", description="A sufficiently long role description for deletion."))
    db_session.commit()

    response = delete_account(user=user, session=db_session)

    assert response.status_code == 204
    assert db_session.query(User).filter(User.email == "delete@example.com").one_or_none() is None
    assert db_session.query(Resume).count() == 0
    assert db_session.query(Job).count() == 0
