from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.config import get_settings
from app.db.session import get_db_session
from app.models import User
from app.schemas.auth import AuthenticatedUserResponse, LoginRequest, SignupRequest, TokenResponse
from app.security.rate_limit import enforce_auth_rate_limit
from app.services.auth import SESSION_COOKIE_NAME, create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth")


def _user_response(user: User) -> AuthenticatedUserResponse:
    return AuthenticatedUserResponse(id=user.id, email=user.email, display_name=user.display_name)


def _set_session_cookie(response: Response, access_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.app_env.lower() == "production",
        samesite="lax",
        path="/",
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: Request, response: Response, payload: SignupRequest, session: Session = Depends(get_db_session)) -> TokenResponse:
    normalized_email = str(payload.email).lower()
    enforce_auth_rate_limit(request, normalized_email)
    user = User(email=normalized_email, display_name=payload.display_name.strip(), password_hash=hash_password(payload.password))
    session.add(user)
    try:
        session.commit()
        session.refresh(user)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account already exists for this email address.") from exc
    access_token = create_access_token(user.id, user.email)
    _set_session_cookie(response, access_token)
    return TokenResponse(access_token=access_token, user=_user_response(user))


@router.post("/login", response_model=TokenResponse)
def login(request: Request, response: Response, payload: LoginRequest, session: Session = Depends(get_db_session)) -> TokenResponse:
    normalized_email = str(payload.email).lower()
    enforce_auth_rate_limit(request, normalized_email)
    user = session.query(User).filter(User.email == normalized_email).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive.")
    access_token = create_access_token(user.id, user.email)
    _set_session_cookie(response, access_token)
    return TokenResponse(access_token=access_token, user=_user_response(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")


@router.get("/me", response_model=AuthenticatedUserResponse)
def me(user: User = Depends(get_current_user)) -> AuthenticatedUserResponse:
    return _user_response(user)
