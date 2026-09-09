import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from apps.services.auth_service.app.domain.roles import UserRole, UserStatus


class UserRegisterRequest(BaseModel):
    """
    Data Transfer Object (DTO) for User Registration.

    Design Pattern:
    - DTO Pattern: Strict contract defining what data clients must provide.
    - Defense-in-Depth Validation: Enforces RFC email format, whitespace normalization,
      and strict password entropy requirements (uppercase, lowercase, number, special char).
    """

    email: EmailStr = Field(..., description="Valid corporate email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="Plaintext password, 8-128 characters"
    )
    role: UserRole = Field(
        default=UserRole.SALES_USER,
        description="Initial RBAC role (OWNER, ADMIN, SALES_USER)",
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Sanitizes email by stripping whitespace and downcasing."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Enforces password complexity:
        - At least 1 lowercase letter
        - At least 1 uppercase letter
        - At least 1 digit
        - At least 1 special character
        """
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?~]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLoginRequest(BaseModel):
    """DTO for User Authentication."""

    email: EmailStr = Field(..., description="User's registered email")
    password: str = Field(..., description="Account password")


class TokenRefreshRequest(BaseModel):
    """DTO for Token Session Refresh."""

    refresh_token: str = Field(..., description="High-entropy raw refresh token issued on login")


class UserLogoutRequest(BaseModel):
    """DTO for Session Termination."""

    refresh_token: str = Field(..., description="Active refresh token to invalidate")


class TokenResponse(BaseModel):
    """DTO returning the minted token pair to clients."""

    access_token: str = Field(..., description="Short-lived signed JWT access token")
    refresh_token: str = Field(..., description="Opaque long-lived refresh token")
    token_type: str = Field(default="bearer", description="Token authentication scheme")
    expires_in: int = Field(..., description="Access token expiration window in seconds")


class UserResponse(BaseModel):
    """
    Sanitized User Representation.
    Security: Never exposes hashed passwords or internal database salt columns.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    is_active: bool
    created_at: datetime


class MessageResponse(BaseModel):
    """Generic status response DTO."""

    message: str


class PasswordResetRequest(BaseModel):
    """
    DTO requesting password reset link/token.
    Anti-Enumeration: Endpoint always returns 200 OK regardless of email existence.
    """

    email: EmailStr = Field(..., description="Registered account email")

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class PasswordResetConfirmRequest(BaseModel):
    """
    DTO confirming password reset with received token and new password.
    Enforces strict password complexity.
    """

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password, 8-128 chars"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?~]", v):
            raise ValueError("Password must contain at least one special character")
        return v
