"""Testes do rate limiting nas rotas sensíveis (slowapi)."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models.refresh_token  # noqa: F401
import app.models.user  # noqa: F401
from app.core.config import settings
from app.core.db import Base, get_db
from app.core.rate_limit import limiter
from app.main import app


@pytest.fixture()
def rate_limited_client() -> Generator[TestClient, None, None]:
    """Client com rate limiting LIGADO e contador zerado."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = testing_session()

    def override_get_db() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()
    limiter.enabled = True
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        limiter.reset()
        limiter.enabled = True
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_login_excede_rate_limit_retorna_429(rate_limited_client: TestClient) -> None:
    limit_per_minute = int(settings.rate_limit_auth.split("/")[0])
    payload = {"email": "rate@example.com", "password": "qualquer-coisa-1"}

    # Esgota o limite (respostas 401 por credencial inválida ainda contam).
    for _ in range(limit_per_minute):
        resp = rate_limited_client.post("/auth/login", json=payload)
        assert resp.status_code != 429

    # A próxima requisição deve estourar o limite.
    blocked = rate_limited_client.post("/auth/login", json=payload)
    assert blocked.status_code == 429
