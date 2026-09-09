from dataclasses import dataclass
from uuid import UUID

from shared.security.roles import UserRole


@dataclass(frozen=True)
class UserPrincipal:
    """
    Authenticated User Principal.

    Design Patterns & Engineering Principles:
    - Principal Pattern / Identity Object: Standardized representation of the authenticated subject
      passed across architectural layers (API -> Application -> Domain).
    - Immutability Pattern (frozen=True): Prevents tampering or state mutation of security context
      during request execution.
    - Information Hiding / Separation of Concerns: Downstream microservices only receive identity
      attributes needed for business decisions (ID, email, role, active workspace). No database
      credentials or password hashes are ever leaked.
    """

    id: UUID
    email: str
    role: UserRole
    workspace_id: UUID | None = None

    def has_role(self, *allowed_roles: UserRole) -> bool:
        """Helper method to check if the principal possesses any of the permitted roles."""
        return self.role in allowed_roles
