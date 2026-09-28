"""Acesso a dados de refresh tokens (camada de repositório, PROJECT.md §5)."""

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """Encapsula a persistência e as consultas de ``RefreshToken``."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.execute(stmt).scalar_one_or_none()

    def revoke(self, token: RefreshToken) -> None:
        token.revoked = True
        self.db.add(token)
        self.db.commit()

    def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True)
        )
        self.db.execute(stmt)
        self.db.commit()
