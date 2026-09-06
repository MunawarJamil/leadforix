from enum import Enum


class UserRole(str, Enum):
    

    OWNER = "OWNER"            # Full organizational & billing authority
    ADMIN = "ADMIN"            # Administrative authority across workspace settings
    SALES_USER = "SALES_USER"  # Standard SDR user conducting research and outreach

    AGENT = "AGENT"            # AI Agent
