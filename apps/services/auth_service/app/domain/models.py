from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from apps.services.auth_service.app.domain.roles import UserRole, UserStatus


@dataclass(frozen=True)
class User:
    """
    Pure Domain Entity representing an authenticated User.

    Design Patterns & Principles:
    - Clean Architecture (Enterprise Business Rules): Completely independent of ORM or HTTP frameworks.
    - Immutability Pattern (frozen=True): Prevents accidental state mutation outside of domain services.
    - Encapsulation: Groups identity, credential hashes, authorization roles, and account lifecycle state.
    """

    id: UUID
    email: str
    hashed_password: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    status: UserStatus = UserStatus.ACTIVE


@dataclass(frozen=True)
class RefreshToken:
    """
    Domain Entity representing an issued cryptographic refresh token.

    Design Pattern:
    - Token Rotation Security: We persist the SHA-256 hash of the token, never the raw token itself,
      so database exposure cannot compromise active sessions.
    """

    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    is_revoked: bool
    created_at: datetime


@dataclass(frozen=True)
class PasswordResetToken:
    """
    Domain Entity representing an issued cryptographic password reset token.

    Design Patterns & Principles:
    - Defense-in-Depth: Persists deterministic SHA-256 hash of high-entropy token.
    - Single-Use Invalidation: Flagged as is_used once consumed.
    """

    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    is_used: bool
    created_at: datetime
