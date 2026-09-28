"""Rotas de health check — usadas para verificar se a aplicação e o banco respondem."""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.db import engine

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict[str, str]:
    """Liveness: a API está de pé."""
    return {"status": "ok"}


@router.get("/db")
def health_db() -> dict[str, str]:
    """Readiness: o banco está acessível."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception as exc:  # noqa: BLE001 - queremos reportar qualquer falha de conexão
        return {"database": "error", "detail": str(exc)}
