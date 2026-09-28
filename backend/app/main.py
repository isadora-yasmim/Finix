"""Ponto de entrada da API do Finix."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.rate_limit import limiter

app = FastAPI(
    title=f"{settings.project_name} API",
    version=settings.version,
    description="Agente financeiro pessoal — importa extratos, categoriza e gera insights.",
)

# Rate limiting (slowapi): registra o limiter e o handler de 429.
app.state.limiter = limiter
# slowapi tipa o handler de forma mais estrita que o Starlette espera; ignore pontual.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)


def api_info() -> dict[str, str]:
    return {
        "name": settings.project_name,
        "version": settings.version,
        "status": "ok",
        "docs": "/docs",
    }


def configure_frontend(application: FastAPI, static_dir: str) -> None:
    """Em produção a mesma imagem serve a API e o build do frontend (mesma origem).

    Com ``static_dir`` vazio ou inexistente (desenvolvimento/testes), a raiz "/"
    devolve as informações da API; caso contrário, devolve a SPA. O mount entra por
    último, então as rotas da API (/health, /auth, /docs...) continuam tendo prioridade.
    """
    directory = Path(static_dir) if static_dir else None
    if directory is not None and directory.is_dir():
        application.add_api_route("/api", api_info, methods=["GET"], tags=["root"])
        application.mount("/", StaticFiles(directory=directory, html=True), name="frontend")
    else:
        application.add_api_route("/", api_info, methods=["GET"], tags=["root"])


configure_frontend(app, settings.static_dir)
