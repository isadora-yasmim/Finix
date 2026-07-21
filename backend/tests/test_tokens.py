"""Testes unitários dos helpers de token (JWT de acesso e refresh opaco)."""

from app.core.tokens import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_refresh_token,
)


def test_access_token_roundtrip() -> None:
    token = create_access_token("user-123")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_decode_token_invalido_retorna_none() -> None:
    assert decode_access_token("nao-e-jwt") is None


def test_refresh_token_e_aleatorio_e_hash_estavel() -> None:
    a = generate_refresh_token()
    b = generate_refresh_token()
    assert a != b
    # O hash é determinístico (mesma entrada → mesmo hash) e de 64 hex chars (SHA-256).
    assert hash_refresh_token(a) == hash_refresh_token(a)
    assert len(hash_refresh_token(a)) == 64
    assert hash_refresh_token(a) != hash_refresh_token(b)
