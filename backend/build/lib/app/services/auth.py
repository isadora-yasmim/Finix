"""Regras de negócio de sessão: emissão, rotação e revogação de tokens (PROJECT.md §5/§10).

Compõe o ``UserService`` (autenticação de credenciais) com o repositório de
refresh tokens. O fluxo de refresh usa **rotação**: a cada renovação o token
antigo é revogado e um novo é emitido. Se um token já revogado for reapresentado,
revogamos toda a família do usuário (detecção de reuso).
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.config import settings
from app.core.tokens import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    refresh_expires_at,
)
from app.models.user import User
from app.repositories.refresh_token import RefreshTokenRepository
from app.schemas.user import UserLogin
from app.services.user import UserService


class InvalidRefreshTokenError(Exception):
    """Refresh token ausente, inválido, expirado ou revogado."""


@dataclass(frozen=True)
class IssuedTokens:
    """Par de tokens recém-emitido. ``refresh_token`` é o valor opaco em texto."""

    user: User
    access_token: str
    refresh_token: str
    access_expires_in: int


class AuthService:
    """Orquestra login, renovação (rotação) e logout."""

    def __init__(self, users: UserService, refresh_repo: RefreshTokenRepository) -> None:
        self.users = users
        self.refresh_repo = refresh_repo

    def login(self, data: UserLogin) -> IssuedTokens:
        """Valida credenciais (pode levantar ``InvalidCredentialsError``) e emite tokens."""
        user = self.users.authenticate(data)
        return self._issue(user)

    def refresh(self, refresh_token: str | None) -> IssuedTokens:
        """Valida o refresh token, rotaciona e emite um novo par."""
        if not refresh_token:
            raise InvalidRefreshTokenError

        stored = self.refresh_repo.get_by_hash(hash_refresh_token(refresh_token))
        if stored is None:
            raise InvalidRefreshTokenError

        # Reuso de token já revogado → trata como comprometimento: revoga tudo.
        if stored.revoked:
            self.refresh_repo.revoke_all_for_user(stored.user_id)
            raise InvalidRefreshTokenError

        if self._is_expired(stored.expires_at):
            raise InvalidRefreshTokenError

        user = self.users.repository.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            raise InvalidRefreshTokenError

        # Rotação: revoga o antigo e emite um novo.
        self.refresh_repo.revoke(stored)
        return self._issue(user)

    def logout(self, refresh_token: str | None) -> None:
        """Revoga o refresh token apresentado (idempotente)."""
        if not refresh_token:
            return
        stored = self.refresh_repo.get_by_hash(hash_refresh_token(refresh_token))
        if stored is not None and not stored.revoked:
            self.refresh_repo.revoke(stored)

    def _issue(self, user: User) -> IssuedTokens:
        access = create_access_token(str(user.id))
        refresh_plain = generate_refresh_token()
        self.refresh_repo.create(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_plain),
            expires_at=refresh_expires_at(),
        )
        return IssuedTokens(
            user=user,
            access_token=access,
            refresh_token=refresh_plain,
            access_expires_in=settings.access_token_expire_minutes * 60,
        )

    @staticmethod
    def _is_expired(expires_at: datetime) -> bool:
        # Tokens vindos do SQLite podem ser naive; normaliza para UTC ciente.
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return expires_at <= datetime.now(UTC)
