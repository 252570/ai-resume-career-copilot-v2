from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models import User
from app.services.auth import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), session: Session = Depends(get_db_session)) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required.")
    user = session.get(User, decode_access_token(credentials.credentials))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user is unavailable.")
    return user


def get_optional_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), session: Session = Depends(get_db_session)) -> User | None:
    if credentials is None:
        return None
    user = session.get(User, decode_access_token(credentials.credentials))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user is unavailable.")
    return user


def assert_record_access(owner_id, user: User | None) -> None:
    """Hide user-owned records from other users while retaining legacy anonymous records."""
    if owner_id is not None and (user is None or owner_id != user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")
