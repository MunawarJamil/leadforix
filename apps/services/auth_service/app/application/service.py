import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from apps.services.auth_service.app.domain.models import RefreshToken, User
from apps.services.auth_service.app.domain.roles import UserRole
from apps.services.auth_service.app.infrastructure.config import get_auth_settings
from apps.services.auth_service.app.infrastructure.repository import AuthRepository
from apps.services.auth_service.app.infrastructure.security import PasswordHasher, TokenService
from shared.exceptions import AuthenticationError, ConflictError


@dataclass(frozen=True)
class TokenPair:
    """DTO containing the generated access and refresh tokens returned to clients."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # in seconds (15 minutes)


class AuthService:
    """
    Application Service orchestrating Authentication & Token Lifecycles.

    Design Patterns & Principles:
    - Service Layer Pattern / Facade: Coordinates domain logic, repositories, and security utilities.
    - Token Rotation Pattern: When refreshing, the old refresh token is immediately revoked and a new pair is issued.
    - Security Enumeration Defense: Authentication failures use uniform error messages.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repo = AuthRepository(session)
        self._hasher = PasswordHasher()
        self._token_service = TokenService()
        self._settings = get_auth_settings()

    async def register_user(
        self,
        email: str,
        password: str,
        role: UserRole = UserRole.SALES_USER,
    ) -> User:
        """
        Registers a new user in the system.
        Enforces unique email and stores only salted bcrypt password hashes.
        """
        normalized_email = email.lower().strip()
        existing = await self._repo.get_user_by_email(normalized_email)
        if existing:
            raise ConflictError(f"User with email '{normalized_email}' already exists")

        now = datetime.now(timezone.utc)
        user = User(
            id=uuid.uuid4(),
            email=normalized_email,
            hashed_password=self._hasher.hash_password(password),
            role=role,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        return await self._repo.create_user(user)

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> tuple[TokenPair, User]:
        """
        Authenticates credentials and issues a fresh token pair.
        """
        user = await self._repo.get_user_by_email(email)
        if not user or not self._hasher.verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        tokens = await self._issue_token_pair(user)
        return tokens, user

    async def refresh_session(self, raw_refresh_token: str) -> tuple[TokenPair, User]:
        """
        Validates refresh token and issues rotated tokens.
        Design: Single-Use Token Rotation mitigates replay and token leakage attacks.
        """
        token_hash = self._token_service.hash_token(raw_refresh_token)
        stored_token = await self._repo.get_refresh_token_by_hash(token_hash)

        if not stored_token or stored_token.is_revoked:
            raise AuthenticationError("Invalid or revoked refresh token")

        if stored_token.expires_at < datetime.now(timezone.utc):
            raise AuthenticationError("Refresh token has expired")

        user = await self._repo.get_user_by_id(stored_token.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User account is no longer active")

        # Invalidate old refresh token (Token Rotation)
        await self._repo.revoke_refresh_token(token_hash)

        # Issue new token pair
        new_tokens = await self._issue_token_pair(user)
        return new_tokens, user

    async def logout_user(self, raw_refresh_token: str) -> None:
        """Revokes a refresh token, terminating the active session."""
        token_hash = self._token_service.hash_token(raw_refresh_token)
        await self._repo.revoke_refresh_token(token_hash)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Fetches user profile for protected /me endpoint."""
        return await self._repo.get_user_by_id(user_id)

    async def _issue_token_pair(self, user: User) -> TokenPair:
        """Internal helper to mint access and refresh tokens and persist token hash."""
        access_token = self._token_service.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        raw_refresh, token_hash, expires_at = self._token_service.generate_refresh_token()

        db_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
            created_at=datetime.now(timezone.utc),
        )
        await self._repo.create_refresh_token(db_token)

        return TokenPair(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_in=self._settings.access_token_expire_minutes * 60,
        )
