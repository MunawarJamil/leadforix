from enum import Enum


class UserRole(str, Enum):
    OWNER = "OWNER"  # Full organizational & billing authority
    ADMIN = "ADMIN"  # Administrative authority across workspace settings
    SALES_USER = "SALES_USER"  # Standard SDR user conducting research and outreach
    AGENT = "AGENT"  # AI Agent


class UserStatus(str, Enum):
    """
    Account Lifecycle States.

    Design Pattern: State Pattern / Value Enum
    - ACTIVE: Standard operational status with full access.
    - SUSPENDED: Temporarily or permanently disabled by an admin (login & refresh blocked).
    - PENDING_VERIFICATION: Registered but awaiting initial identity/email confirmation.
    """

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
