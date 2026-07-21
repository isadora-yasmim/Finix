"""Testes do fluxo JWT: rota protegida, refresh com rotação e logout."""

from fastapi.testclient import TestClient


def _signup_and_login(client: TestClient, email: str = "jwt@example.com") -> str:
    client.post("/auth/signup", json={"email": email, "password": "senha-correta-1"})
    resp = client.post("/auth/login", json={"email": email, "password": "senha-correta-1"})
    assert resp.status_code == 200
    return str(resp.json()["access_token"])


def test_me_sem_token_retorna_401(client: TestClient) -> None:
    assert client.get("/auth/me").status_code == 401


def test_me_com_token_invalido_retorna_401(client: TestClient) -> None:
    resp = client.get("/auth/me", headers={"Authorization": "Bearer nao-e-um-jwt"})
    assert resp.status_code == 401


def test_me_com_token_valido_retorna_usuario(client: TestClient) -> None:
    token = _signup_and_login(client)
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "jwt@example.com"


def test_refresh_emite_novo_access_token(client: TestClient) -> None:
    _signup_and_login(client)  # cookie de refresh fica no client
    resp = client.post("/auth/refresh")
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    # O novo access token deve funcionar numa rota protegida.
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200


def test_refresh_sem_cookie_retorna_401(client: TestClient) -> None:
    assert client.post("/auth/refresh").status_code == 401


def test_refresh_rotaciona_invalida_token_antigo(client: TestClient) -> None:
    _signup_and_login(client)
    old_refresh = client.cookies.get("finix_refresh")
    assert old_refresh is not None

    # Primeira renovação: rotaciona o refresh (define um novo cookie).
    assert client.post("/auth/refresh").status_code == 200

    # Reapresentar o refresh ANTIGO deve falhar (foi revogado na rotação).
    client.cookies.set("finix_refresh", old_refresh)
    assert client.post("/auth/refresh").status_code == 401


def test_logout_revoga_refresh(client: TestClient) -> None:
    _signup_and_login(client)
    assert client.post("/auth/logout").status_code == 204
    # Após logout, o refresh não vale mais.
    assert client.post("/auth/refresh").status_code == 401
