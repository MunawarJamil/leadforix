from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from apps.services.workspace_service.app.domain.roles import TenantType, WorkspaceRole


@dataclass(frozen=True)
class Workspace:
    """
    Domain Entity representing a tenant Workspace boundary.

    Design Patterns & Principles:
    - Clean Architecture: Completely decoupled from ORM and HTTP layers.
    - Immutability Pattern (frozen=True): Protects internal state from side-effects.
    - Multi-Tenancy Scope: Explicit tenant_type and owner_id for authorization.
    """

    id: UUID
    name: str
    slug: str
    owner_id: UUID
    tenant_type: TenantType
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class WorkspaceMember:
    """
    Domain Entity representing user membership inside a Workspace.

    Design Patterns & Principles:
    - Tenancy Boundary: Associates a user_id with a specific workspace and role.
    """

    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: WorkspaceRole
    joined_at: datetime
