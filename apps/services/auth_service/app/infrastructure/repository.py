import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.services.auth_service.app.domain.models import RefreshToken, User
from apps.services.auth_service.app.infrastructure.models import RefreshTokenModel, UserModel


class AuthRepository:
    """
    Data Access Layer for Users and Session Tokens.

    Design Patterns & Principles:
    - Repository Pattern: Mediates between the domain and database mapping layers, providing
      a clean in-memory-like collection interface for accessing entities.
    - Dependency Injection: Receives the active AsyncSession, participating in transactions
      managed by the caller.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieves a user by unique email address."""
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Retrieves a user by primary key UUID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def create_user(self, user: User) -> User:
        """Persists a new user record in the database."""
        user_model = UserModel.from_domain(user)
        self._session.add(user_model)
        await self._session.flush()
        return user_model.to_domain()

    async def create_refresh_token(self, token: RefreshToken) -> RefreshToken:
        """Persists a new refresh token record."""
        token_model = RefreshTokenModel(
            id=token.id,
            user_id=token.user_id,
            token_hash=token.token_hash,
            expires_at=token.expires_at,
            is_revoked=token.is_revoked,
            created_at=token.created_at,
        )
        self._session.add(token_model)
        await self._session.flush()
        return token_model.to_domain()

    async def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Looks up a refresh token by its SHA-256 digest."""
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        result = await self._session.execute(stmt)
        token_model = result.scalar_one_or_none()
        return token_model.to_domain() if token_model else None

    async def revoke_refresh_token(self, token_hash: str) -> bool:
        """Marks a refresh token as revoked (used during token rotation and logout)."""
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .values(is_revoked=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0
