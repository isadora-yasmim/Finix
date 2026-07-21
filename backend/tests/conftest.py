"""Fixtures de teste: banco SQLite isolado e TestClient com get_db sobrescrito."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models.refresh_token  # noqa: F401  (registra o modelo em Base.metadata)
import app.models.user  # noqa: F401  (registra o modelo em Base.metadata)
from app.core.db import Base, get_db
from app.core.rate_limit import limiter
from app.main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """SQLite em memória, criado e destruído a cada teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient com a dependency get_db apontando para o SQLite de teste.

    O rate limiting fica DESLIGADO por padrão para não interferir nos testes
    funcionais; o teste de rate limit o reativa explicitamente.
    """

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    limiter.enabled = False
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    limiter.reset()
    limiter.enabled = True
