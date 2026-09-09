from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from apps.services.auth_service.app.domain.roles import UserRole


class UserRegisterRequest(BaseModel):
    """
    Data Transfer Object (DTO) for User Registration.

    Design Pattern:
    - DTO Pattern: Strict contract defining what data clients must provide.
    - Input Sanitization & Validation: Enforces RFC email format and minimum password length.
    """

    email: EmailStr = Field(..., description="Valid corporate email address")
    password: str = Field(..., min_length=8, description="Plaintext password, minimum 8 characters")
    role: UserRole = Field(
        default=UserRole.SALES_USER,
        description="Initial RBAC role (OWNER, ADMIN, SALES_USER)",
    )


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
    is_active: bool
    created_at: datetime


class MessageResponse(BaseModel):
    """Generic status response DTO."""

    message: str
