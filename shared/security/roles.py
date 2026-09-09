from enum import Enum


class UserRole(str, Enum):
    """
    Platform-wide Role-Based Access Control (RBAC) Roles.

    Design Patterns & Principles:
    - Value Object / Enum Pattern: Canonical authorization definitions shared across
      all microservices and gateway filters.
    - Architectural Separation: Defined in shared/security so downstream microservices
      do not depend on the internal domain package of auth_service.
    """

    OWNER = "OWNER"  # Full organizational & billing authority
    ADMIN = "ADMIN"  # Administrative authority across workspace settings
    SALES_USER = "SALES_USER"  # Standard SDR user conducting research and outreach
    AGENT = "AGENT"  # AI Agent autonomous execution role
