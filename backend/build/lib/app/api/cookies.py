"""Helpers para o cookie do refresh token (HttpOnly + Secure + SameSite, PROJECT.md §10)."""

from fastapi import Response

from app.core.config import settings


def set_refresh_cookie(response: Response, token: str) -> None:
    """Grava o refresh token em cookie HttpOnly, restrito ao path de auth."""
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,  # type: ignore[arg-type]
        path=settings.refresh_cookie_path,
    )


def clear_refresh_cookie(response: Response) -> None:
    """Remove o cookie do refresh token (logout)."""
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=settings.refresh_cookie_path,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,  # type: ignore[arg-type]
    )
