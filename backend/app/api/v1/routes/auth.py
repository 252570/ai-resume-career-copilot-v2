from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db_session
from app.models import User
from app.schemas.auth import AuthenticatedUserResponse, LoginRequest, SignupRequest, TokenResponse
from app.services.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth")


def _user_response(user: User) -> AuthenticatedUserResponse:
    return AuthenticatedUserResponse(id=user.id, email=user.email, display_name=user.display_name)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, session: Session = Depends(get_db_session)) -> TokenResponse:
    user = User(email=str(payload.email).lower(), display_name=payload.display_name.strip(), password_hash=hash_password(payload.password))
    session.add(user)
    try:
        session.commit()
        session.refresh(user)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account already exists for this email address.") from exc
    return TokenResponse(access_token=create_access_token(user.id, user.email), user=_user_response(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_db_session)) -> TokenResponse:
    user = session.query(User).filter(User.email == str(payload.email).lower()).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive.")
    return TokenResponse(access_token=create_access_token(user.id, user.email), user=_user_response(user))


@router.get("/me", response_model=AuthenticatedUserResponse)
def me(user: User = Depends(get_current_user)) -> AuthenticatedUserResponse:
    return _user_response(user)
