from fastapi import APIRouter, Depends, status

from apps.services.auth_service.app.api.dependencies import get_auth_service, get_current_user
from apps.services.auth_service.app.api.schemas import (
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserLogoutRequest,
    UserRegisterRequest,
    UserResponse,
)
from apps.services.auth_service.app.application.service import AuthService
from apps.services.auth_service.app.domain.models import User

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Creates a new user profile with salted bcrypt password."""
    user = await auth_service.register_user(
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue token pair",
)
async def login(
    payload: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Verifies credentials and issues short-lived JWT access token and long-lived refresh token."""
    tokens, _ = await auth_service.authenticate_user(
        email=payload.email,
        password=payload.password,
    )
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate tokens using valid refresh token",
)
async def refresh(
    payload: TokenRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Validates refresh token, invalidates old token, and returns a fresh token pair."""
    tokens, _ = await auth_service.refresh_session(payload.refresh_token)
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Terminate session and revoke refresh token",
)
async def logout(
    payload: UserLogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Revokes refresh token so it cannot be used to refresh access tokens."""
    await auth_service.logout_user(payload.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get profile of currently authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Protected endpoint returning identity & role of authenticated caller."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/password-reset/request",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request a password reset link/token",
)
async def request_password_reset(
    payload: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Anti-Enumeration Endpoint:
    Always returns 200 OK regardless of whether the email exists in the database,
    preventing account enumeration reconnaissance attacks.
    """
    await auth_service.request_password_reset(payload.email)
    return MessageResponse(
        message="If an account exists with this email, password reset instructions have been sent."
    )


@router.post(
    "/password-reset/confirm",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm password reset with valid token",
)
async def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Validates reset token, applies new password, invalidates the token,
    and terminates all existing active sessions.
    """
    await auth_service.confirm_password_reset(
        raw_token=payload.token,
        new_password=payload.new_password,
    )
    return MessageResponse(
        message="Password successfully reset. Please log in with your new credentials."
    )
