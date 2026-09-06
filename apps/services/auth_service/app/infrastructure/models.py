import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.services.auth_service.app.domain.models import RefreshToken, User
from apps.services.auth_service.app.domain.roles import UserRole
from shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQLAlchemy ORM Model representing the 'users' database table.

    Design Patterns & Principles:
    - Data Mapper Pattern: Separates the persistence schema from the pure domain entity (User).
    - Separation of Concerns: Database constraints (indexes, cascades, nullability) are declared
      here, keeping domain entities decoupled from SQL dialects.
    - Security: Email is unique-indexed for O(1) lookups; passwords store one-way bcrypt hashes.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=UserRole.SALES_USER.value,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # 1-to-Many relationship with cascade deletion: Deleting a user purges all active refresh tokens
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_domain(self) -> User:
        """Translates persistence ORM model to pure Domain entity."""
        return User(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            role=UserRole(self.role),
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        """Factory Method creating ORM model from a Domain entity."""
        return cls(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class RefreshTokenModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQLAlchemy ORM Model representing issued refresh tokens for session management.

    Design Patterns & Security Principles:
    - Cryptographic Token Hashing: We store a 64-character SHA-256 hash of the refresh token.
      Even if the database is dumped, tokens cannot be forged or reused.
    - Cascade Invalidation: Linked via Foreign Key to users.id with ON DELETE CASCADE.
    - Index Optimization: Indexed token_hash and expires_at for fast revocation and session checks.
    """

    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False,
    )

    user: Mapped["UserModel"] = relationship(
        back_populates="refresh_tokens",
    )

    def to_domain(self) -> RefreshToken:
        """Translates persistence ORM model to pure Domain entity."""
        return RefreshToken(
            id=self.id,
            user_id=self.user_id,
            token_hash=self.token_hash,
            expires_at=self.expires_at,
            is_revoked=self.is_revoked,
            created_at=self.created_at,
        )
