"""Testes do que a pipeline de CI/CD depende para implantar a aplicação."""

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app, configure_frontend


def test_health_version_expoe_commit_e_ambiente() -> None:
    resp = TestClient(app).get("/health/version")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == {"version", "commit", "environment"}
    assert body["commit"] == "dev"  # fora da imagem Docker não há GIT_SHA


@pytest.mark.parametrize(
    "raw",
    [
        "postgres://u:p@host.neon.tech/finix?sslmode=require",
        "postgresql://u:p@host.neon.tech/finix?sslmode=require",
        "postgresql+psycopg://u:p@host.neon.tech/finix?sslmode=require",
    ],
)
def test_database_url_recebe_driver_psycopg(raw: str) -> None:
    settings = Settings(database_url=raw)
    assert settings.database_url == "postgresql+psycopg://u:p@host.neon.tech/finix?sslmode=require"


def test_sem_frontend_a_raiz_devolve_info_da_api() -> None:
    application = FastAPI()
    configure_frontend(application, "")
    resp = TestClient(application).get("/")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Finix"


def test_com_frontend_a_raiz_devolve_a_spa_e_a_api_continua_acessivel(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("<title>Finix</title>", encoding="utf-8")
    application = FastAPI()

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    configure_frontend(application, str(tmp_path))
    client = TestClient(application)

    assert "<title>Finix</title>" in client.get("/").text
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api").json()["status"] == "ok"
