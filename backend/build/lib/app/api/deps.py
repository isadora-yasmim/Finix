"""Dependências compartilhadas da camada de API (auth, sessão, serviços)."""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.tokens import decode_access_token
from app.models.user import User
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.user import UserService

SessionDep = Annotated[Session, Depends(get_db)]

# auto_error=False: tratamos a ausência do header nós mesmos (401 padronizado).
_bearer_scheme = HTTPBearer(auto_error=False)
BearerDep = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)]

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não autenticado.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_user_service(db: SessionDep) -> UserService:
    """Monta o serviço de usuário com a sessão do request."""
    return UserService(UserRepository(db))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_auth_service(users: UserServiceDep, db: SessionDep) -> AuthService:
    """Monta o serviço de autenticação (login/refresh/logout)."""
    return AuthService(users, RefreshTokenRepository(db))


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(credentials: BearerDep, db: SessionDep) -> User:
    """Resolve o usuário autenticado a partir do JWT no header ``Authorization``."""
    if credentials is None:
        raise _CREDENTIALS_EXCEPTION

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise _CREDENTIALS_EXCEPTION

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise _CREDENTIALS_EXCEPTION

    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise _CREDENTIALS_EXCEPTION from None

    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise _CREDENTIALS_EXCEPTION

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
