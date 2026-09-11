import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.services.auth_service.app.domain.models import (
    PasswordResetToken,
    RefreshToken,
    User,
)
from apps.services.auth_service.app.domain.roles import UserStatus
from apps.services.auth_service.app.infrastructure.models import (
    PasswordResetTokenModel,
    RefreshTokenModel,
    UserModel,
)


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




    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> int:
        """
        Revokes all active refresh tokens belonging to a user.
        Used during security incident mitigation (token reuse detection) and password resets.
        """
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.is_revoked.is_(False),
            )
            .values(is_revoked=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    async def create_password_reset_token(self, token: PasswordResetToken) -> PasswordResetToken:
        """Persists a new password reset token."""
        token_model = PasswordResetTokenModel(
            id=token.id,
            user_id=token.user_id,
            token_hash=token.token_hash,
            expires_at=token.expires_at,
            is_used=token.is_used,
            created_at=token.created_at,
        )
        self._session.add(token_model)
        await self._session.flush()
        return token_model.to_domain()

    async def get_password_reset_token_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        """Retrieves a reset token record by its SHA-256 digest."""
        stmt = select(PasswordResetTokenModel).where(
            PasswordResetTokenModel.token_hash == token_hash
        )
        result = await self._session.execute(stmt)
        token_model = result.scalar_one_or_none()
        return token_model.to_domain() if token_model else None

    async def mark_password_reset_token_used(self, token_hash: str) -> bool:
        """Marks a password reset token as used (single-use enforcement)."""
        stmt = (
            update(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.token_hash == token_hash)
            .values(is_used=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def update_user_password(self, user_id: uuid.UUID, new_hashed_password: str) -> bool:
        """Updates the stored bcrypt password hash for a user."""
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(hashed_password=new_hashed_password)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def update_user_status(self, user_id: uuid.UUID, status: UserStatus) -> bool:
        """Updates the lifecycle status of a user."""
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(status=status.value)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0
