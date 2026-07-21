"""Ponto de entrada da API do Finix."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "name": settings.project_name,
        "version": settings.version,
        "status": "ok",
        "docs": "/docs",
    }
