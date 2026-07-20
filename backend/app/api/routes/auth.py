"""Rotas de autenticação: cadastro e login.

Nesta etapa (Dia 2) o login valida as credenciais e retorna o usuário.
A emissão de tokens JWT entra no Dia 3.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.user import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UserService,
)

router = APIRouter(prefix="/auth", tags=["auth"])

SessionDep = Annotated[Session, Depends(get_db)]


def get_user_service(db: SessionDep) -> UserService:
    """Monta o serviço de usuário com a sessão do request."""
    return UserService(UserRepository(db))


ServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(data: UserCreate, service: ServiceDep) -> UserRead:
    try:
        user = service.register(data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado.",
        ) from None
    return UserRead.model_validate(user)


@router.post("/login", response_model=UserRead)
def login(data: UserLogin, service: ServiceDep) -> UserRead:
    try:
        user = service.authenticate(data)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        ) from None
    return UserRead.model_validate(user)
