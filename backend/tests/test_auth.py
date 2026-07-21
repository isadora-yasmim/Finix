"""Testes dos endpoints de cadastro e login (contrato base)."""

from fastapi.testclient import TestClient


def test_signup_cria_usuario(client: TestClient) -> None:
    resp = client.post(
        "/auth/signup",
        json={"email": "user@example.com", "password": "senha-super-segura"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "user@example.com"
    assert body["is_active"] is True
    assert body["currency"] == "BRL"
    assert "id" in body
    # O hash da senha nunca pode aparecer na resposta.
    assert "password" not in body
    assert "password_hash" not in body


def test_signup_normaliza_email(client: TestClient) -> None:
    resp = client.post(
        "/auth/signup",
        json={"email": "  Maria@Example.COM ", "password": "outra-senha-boa"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "maria@example.com"


def test_signup_email_duplicado_retorna_409(client: TestClient) -> None:
    payload = {"email": "dup@example.com", "password": "senha-valida-123"}
    assert client.post("/auth/signup", json=payload).status_code == 201
    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 409


def test_signup_senha_curta_retorna_422(client: TestClient) -> None:
    resp = client.post(
        "/auth/signup",
        json={"email": "short@example.com", "password": "123"},
    )
    assert resp.status_code == 422


def test_signup_email_invalido_retorna_422(client: TestClient) -> None:
    resp = client.post(
        "/auth/signup",
        json={"email": "nao-e-email", "password": "senha-valida-123"},
    )
    assert resp.status_code == 422


def test_login_com_credenciais_validas_retorna_access_token(client: TestClient) -> None:
    client.post(
        "/auth/signup",
        json={"email": "login@example.com", "password": "senha-correta-1"},
    )
    resp = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "senha-correta-1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] > 0
    # O refresh token vai como cookie HttpOnly, não no corpo.
    assert "refresh_token" not in body
    assert "finix_refresh" in resp.cookies


def test_login_senha_errada_retorna_401(client: TestClient) -> None:
    client.post(
        "/auth/signup",
        json={"email": "wrongpass@example.com", "password": "senha-correta-1"},
    )
    resp = client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "senha-errada-9"},
    )
    assert resp.status_code == 401


def test_login_usuario_inexistente_retorna_401(client: TestClient) -> None:
    resp = client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "qualquer-coisa-1"},
    )
    assert resp.status_code == 401
