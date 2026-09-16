from enum import Enum


class WorkspaceRole(str, Enum):
    """
    RBAC Roles within a Workspace tenant boundary.

    Design Pattern: Value Object / String Enum.
    """

    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class TenantType(str, Enum):
    """
    Multi-tenant context classification for Leadforix platform.

    Design Pattern: Tenant Scope / Classification Enum.
    """

    JOB_SEEKER = "JOB_SEEKER"
    FREELANCER = "FREELANCER"
    AGENCY = "AGENCY"
