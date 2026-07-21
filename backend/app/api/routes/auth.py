"""Rotas de autenticação: cadastro, login, refresh, logout e perfil.

Fluxo de tokens (PROJECT.md §10):
- ``signup`` cria o usuário e retorna a representação pública.
- ``login`` valida credenciais, retorna o **access token** (JWT curto) no corpo e
  grava o **refresh token** em cookie HttpOnly.
- ``refresh`` lê o cookie, rotaciona o refresh e emite um novo access token.
- ``logout`` revoga o refresh token e limpa o cookie.
- ``me`` é protegida por JWT (exemplo de rota autenticada).

As rotas sensíveis (signup/login/refresh) têm rate limiting por IP.
"""

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.api.cookies import clear_refresh_cookie, set_refresh_cookie
from app.api.deps import AuthServiceDep, CurrentUser, UserServiceDep
from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.auth import InvalidRefreshTokenError
from app.services.user import EmailAlreadyRegisteredError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])

_INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas.",
)
_INVALID_REFRESH = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Sessão inválida ou expirada. Faça login novamente.",
)


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_auth)
def signup(request: Request, data: UserCreate, service: UserServiceDep) -> UserRead:
    try:
        user = service.register(data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado.",
        ) from None
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
def login(
    request: Request,
    response: Response,
    data: UserLogin,
    service: AuthServiceDep,
) -> TokenResponse:
    try:
        issued = service.login(data)
    except InvalidCredentialsError:
        raise _INVALID_CREDENTIALS from None

    set_refresh_cookie(response, issued.refresh_token)
    return TokenResponse(
        access_token=issued.access_token,
        expires_in=issued.access_expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
def refresh(request: Request, response: Response, service: AuthServiceDep) -> TokenResponse:
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    try:
        issued = service.refresh(refresh_token)
    except InvalidRefreshTokenError:
        clear_refresh_cookie(response)
        raise _INVALID_REFRESH from None

    set_refresh_cookie(response, issued.refresh_token)
    return TokenResponse(
        access_token=issued.access_token,
        expires_in=issued.access_expires_in,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, service: AuthServiceDep) -> Response:
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    service.logout(refresh_token)
    clear_refresh_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
