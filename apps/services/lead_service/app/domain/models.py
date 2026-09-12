"""
Domain models for the Lead Discovery and Ingestion subsystem.

Design Patterns & Principles:
- Domain-Driven Design (DDD) Value Object: `RawLead` is an immutable, validated
  representation of a discovered opportunity prior to scoring and persistence.
- Type Safety & Encapsulation: Explicit `LeadSource` enum prevents magic strings.
"""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LeadSource(StrEnum):
    """
    Enumeration of external data providers for lead discovery.
    StrEnum guarantees seamless JSON serialization and strict type checking.
    """

    HACKER_NEWS = "hacker_news"
    REMOTIVE = "remotive"


class RawLead(BaseModel):
    """
    Canonical normalized lead entity produced by provider parsers.

    Design Pattern: Value Object (Immutable)
    - frozen=True: Prevents attribute mutation across concurrent pipeline stages.
    - Strict validation: Strips whitespace and guarantees valid data contracts.
    """

    model_config = ConfigDict(frozen=True, extra="ignore")

    company_name: str = Field(..., description="Canonicalized name of hiring company")
    title: str = Field(..., description="Role headline or position title")
    description: str = Field(..., description="Sanitized, plain-text opportunity description")
    source: LeadSource = Field(..., description="Origin provider of the opportunity")
    source_url: str = Field(..., description="Direct permalink or reference URL")
    source_id: str = Field(..., description="Upstream provider's unique ID (e.g. comment/job ID)")
    location: str | None = Field(default=None, description="Extracted geographic location")
    is_remote: bool = Field(default=False, description="Flag indicating if role supports remote work")
    salary_info: str | None = Field(default=None, description="Extracted compensation details if present")
    skills_raw: list[str] = Field(default_factory=list, description="Raw tags or technologies mentioned")
    posted_at: datetime | None = Field(default=None, description="Original publication timestamp")
    discovered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when lead was ingested",
    )
    raw_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Supplemental provider-specific metadata for auditability",
    )

    @field_validator("company_name", "title", "description", mode="before")
    @classmethod
    def strip_and_validate_text(cls, value: Any) -> str:
        """Enforces clean string boundaries and eliminates extraneous whitespace."""
        if not isinstance(value, str):
            value = str(value) if value is not None else ""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or solely whitespace.")
        return cleaned
