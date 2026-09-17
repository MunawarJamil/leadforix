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

class ExperienceLevel(str, Enum):
    """Seniority level for job matching."""

    ENTRY = "ENTRY"
    MID = "MID"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
    ARCHITECT = "ARCHITECT"
    EXPERT = "EXPERT"
    


class JobSearchStatus(str, Enum):
    """Job seeker activity status."""

    ACTIVELY_LOOKING = "ACTIVELY_LOOKING"
    OPEN_TO_OFFERS = "OPEN_TO_OFFERS"
    NOT_LOOKING = "NOT_LOOKING"
