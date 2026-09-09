from apps.services.auth_service.app.domain.roles import UserRole
from uuid import UUID

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared.exceptions import AuthenticationError, AuthorizationError
from shared.security.principal import UserPrincipal
from shared.security.validator import StatelessTokenValidator

# Reusable HTTP Bearer scheme (auto_error=False allows centralized custom 401 exceptions)
bearer_scheme = HTTPBearer(auto_error=False)


def get_token_validator() -> StatelessTokenValidator:
    """Dependency Injection provider for the stateless token validator."""
    return StatelessTokenValidator()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    validator: StatelessTokenValidator = Depends(get_token_validator),
) -> UserPrincipal:
    """
    FastAPI Security Dependency: Authenticates incoming request statelessly.

    Design Pattern: Guard Pattern / Authenticator
    - Extracts token from 'Authorization: Bearer <token>' header.
    - Validates signature and returns immutable UserPrincipal.
    - Raises RFC-compliant AuthenticationError (HTTP 401) on failure.
    """
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Missing or malformed Authorization header")

    return validator.validate_and_extract_principal(credentials.credentials)


def require_roles(*allowed_roles: UserRole):
    """
    FastAPI RBAC Security Dependency Factory.

    Design Pattern: Higher-Order Function / Policy Pattern
    Returns a dependency that asserts the caller possesses at least one of the specified roles.

    Example:
        @router.delete("/leads/{id}", dependencies=[Depends(require_roles("OWNER", "ADMIN"))])
    """

    def role_checker(current_user: UserPrincipal = Depends(get_current_user)) -> UserPrincipal:
        if not current_user.has_role(*allowed_roles):
            raise AuthorizationError(
                f"Role '{current_user.role}' is not authorized to access this resource"
            )
        return current_user

    return role_checker


async def require_workspace(
    current_user: UserPrincipal = Depends(get_current_user),
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-ID"),
) -> UUID:
    """
    FastAPI Multi-Tenancy Dependency: Resolves and enforces active workspace context.

    Design Pattern: Context Resolution Strategy
    - Priority 1: Direct 'workspace_id' claim in the JWT token.
    - Priority 2: 'X-Workspace-ID' HTTP header passed by clients during workspace switching.
    - Rejects request with AuthorizationError (HTTP 403) if no valid workspace context is provided.
    """
    if current_user.workspace_id:
        return current_user.workspace_id

    if x_workspace_id:
        try:
            return UUID(x_workspace_id)
        except ValueError as e:
            raise AuthorizationError("Header 'X-Workspace-ID' contains an invalid UUID") from e

    raise AuthorizationError("Workspace context is required but was not provided")
