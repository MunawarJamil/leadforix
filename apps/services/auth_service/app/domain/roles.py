from enum import Enum

from shared.security.roles import UserRole


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


__all__ = ["UserRole", "UserStatus"]
