"""Ponto de entrada da API do Finix."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=f"{settings.project_name} API",
    version=settings.version,
    description="Agente financeiro pessoal — importa extratos, categoriza e gera insights.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "name": settings.project_name,
        "version": settings.version,
        "status": "ok",
        "docs": "/docs",
    }
