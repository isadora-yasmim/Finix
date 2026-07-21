"""Limiter compartilhado (slowapi) aplicado às rotas sensíveis (PROJECT.md §10).

A chave é o IP de origem. O storage padrão é em memória, suficiente para uma
instância single-tenant (PROJECT.md §3). Pode ser desligado por configuração
(``RATE_LIMIT_ENABLED=false``), útil em testes.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.rate_limit_enabled,
    default_limits=[],
)
