"""Testes unitários do módulo de hashing de senhas."""

from app.core.security import hash_password, verify_password


def test_hash_difere_da_senha_original() -> None:
    hashed = hash_password("minha-senha")
    assert hashed != "minha-senha"
    assert hashed.startswith("$argon2")


def test_hash_eh_salgado_e_unico() -> None:
    assert hash_password("mesma-senha") != hash_password("mesma-senha")


def test_verify_aceita_senha_correta() -> None:
    hashed = hash_password("senha-valida")
    assert verify_password("senha-valida", hashed) is True


def test_verify_rejeita_senha_errada() -> None:
    hashed = hash_password("senha-valida")
    assert verify_password("senha-invalida", hashed) is False


def test_verify_nao_levanta_em_hash_malformado() -> None:
    assert verify_password("qualquer", "nao-e-um-hash-argon2") is False