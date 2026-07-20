"""Hashing e verificação de senhas com Argon2 (argon2-cffi).

A biblioteca é encapsulada atrás de funções simples para que a implementação
possa ser trocada sem afetar o resto da aplicação (PROJECT.md §5/§10).

Argon2id é o algoritmo recomendado pela OWASP para hashing de senhas; usamos
os parâmetros padrão do argon2-cffi, que já seguem essas recomendações.
"""

from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

_hasher = PasswordHasher()

# Hash de uma senha fictícia, calculado uma vez. Usado para equalizar o tempo
# de resposta no login quando o e-mail não existe, evitando um oráculo de
# enumeração de usuários por timing.
_DUMMY_HASH = _hasher.hash("dummy-password-for-constant-time-verification")


def hash_password(plain_password: str) -> str:
    """Gera o hash Argon2id de uma senha em texto puro."""
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica uma senha contra o hash armazenado. Nunca levanta exceção."""
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def dummy_verify() -> None:
    """Executa uma verificação descartável para manter o tempo constante."""
    verify_password("invalid", _DUMMY_HASH)