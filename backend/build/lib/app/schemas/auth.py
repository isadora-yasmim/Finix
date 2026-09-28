"""Schemas de autenticação relacionados a tokens."""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Resposta com o access token. O refresh vai em cookie HttpOnly, não no corpo."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos de validade do access token
