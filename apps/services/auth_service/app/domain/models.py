from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from apps.services.auth_service.app.domain.roles import UserRole


@dataclass(frozen=True)
class User:
    """
    Pure Domain Entity representing an authenticated User.

    Design Patterns & Principles:
    - Clean Architecture (Enterprise Business Rules): Completely independent of ORM or HTTP frameworks.
    - Immutability Pattern (frozen=True): Prevents accidental state mutation outside of domain services.
    - Encapsulation: Groups identity, credential hashes, and authorization roles.
    """

    id: UUID
    email: str
    hashed_password: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


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
