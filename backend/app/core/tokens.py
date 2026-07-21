"""Emissão/verificação de JWT de acesso e geração de refresh tokens opacos.

Estratégia (PROJECT.md §10):

- **Access token**: JWT curto e *stateless* (assinado com ``secret_key``). Carrega
  o ``sub`` (id do usuário) e ``type=access``. Não é persistido.
- **Refresh token**: string opaca de alta entropia, entregue ao cliente via cookie
  HttpOnly. No banco guardamos apenas o **SHA-256** do token (nunca o valor em si),
  o que permite revogar/rotacionar sem armazenar segredo reversível.

Por que SHA-256 no refresh (e Argon2 só na senha)? Refresh tokens já são aleatórios
de alta entropia — não sofrem ataque de dicionário —, então um hash rápido é o
padrão adequado; Argon2 (lento) é necessário apenas para senhas de baixa entropia.
"""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError

from app.core.config import settings


def create_access_token(subject: str) -> str:
    """Gera um JWT de acesso para o ``subject`` (id do usuário em texto)."""
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Valida e decodifica um JWT de acesso. Retorna ``None`` se inválido/expirado."""
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError:
        return None
    if payload.get("type") != "access":
        return None
    return payload


def generate_refresh_token() -> str:
    """Token opaco de alta entropia (enviado ao cliente, nunca persistido em texto)."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """SHA-256 do refresh token — só o hash é persistido no banco."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def refresh_expires_at() -> datetime:
    """Instante de expiração de um novo refresh token."""
    return datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
