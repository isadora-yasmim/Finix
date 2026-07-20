"""Regras de negócio de usuário e autenticação (camada de serviço)."""

from app.core.security import dummy_verify, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin


class EmailAlreadyRegisteredError(Exception):
    """E-mail já está em uso por outro usuário."""


class InvalidCredentialsError(Exception):
    """E-mail e/ou senha inválidos (mensagem genérica por segurança)."""


class UserService:
    """Orquestra cadastro e autenticação sobre o repositório."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def register(self, data: UserCreate) -> User:
        email = self._normalize_email(data.email)
        if self.repository.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError
        return self.repository.create(email=email, password_hash=hash_password(data.password))

    def authenticate(self, data: UserLogin) -> User:
        email = self._normalize_email(data.email)
        user = self.repository.get_by_email(email)

        # Verificação de tempo constante: mesmo sem usuário, gastamos o tempo de
        # um verify para não vazar a existência do e-mail por timing.
        if user is None:
            dummy_verify()
            raise InvalidCredentialsError

        if not verify_password(data.password, user.password_hash) or not user.is_active:
            raise InvalidCredentialsError

        return user

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()
