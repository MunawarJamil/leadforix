from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from apps.services.auth_service.app.application.service import AuthService
from apps.services.auth_service.app.domain.models import User
from apps.services.auth_service.app.domain.roles import UserRole
from apps.services.auth_service.app.infrastructure.security import TokenService
from shared.database import get_db_session
from shared.exceptions import AuthenticationError, AuthorizationError

# HTTP Bearer scheme for parsing Authorization: Bearer <token>
security_scheme = HTTPBearer(auto_error=False)


def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    """
    Dependency Injection provider constructing AuthService with the active request database session.
    """
    return AuthService(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    FastAPI Security Dependency for Protected Endpoints.

    Design Principles:
    - Guard / Authenticator Pattern: Validates bearer token on incoming HTTP requests.
    - Decodes JWT claims, extracts the Subject (UUID), and loads the fresh User from the database.
    - Rejects missing, expired, invalid, or deactivated accounts.
    """
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Missing or malformed Authorization header")

    token_service = TokenService()
    payload = token_service.decode_access_token(credentials.credentials)

    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError) as e:
        raise AuthenticationError("Malformed token subject claim") from e

    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise AuthenticationError("User referenced by token no longer exists")

    if not user.is_active:
        raise AuthenticationError("User account is inactive")

    return user


def require_roles(*allowed_roles: UserRole):
    """
    Design Pattern: Higher-Order Function / Policy Pattern (RBAC Guard)
    Returns a FastAPI dependency that verifies whether the authenticated user possesses
    one of the specified authorization roles.

    Example usage:
        @router.get("/admin-only", dependencies=[Depends(require_roles(UserRole.OWNER, UserRole.ADMIN))])
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationError(
                f"User with role '{current_user.role.value}' lacks required permissions"
            )
        return current_user

    return role_checker
