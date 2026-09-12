"""
Domain models for the Lead Discovery and Ingestion subsystem.

Design Patterns:
- DDD Value Object: Immutable types (`RawLead`, `SkillMatchResult`).
- DDD Entity: Identifiable entity (`Lead`) with UUID lifecycle.
- Factory Method: `Lead.from_raw_lead` encapsulates instantiation logic.
"""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LeadSource(StrEnum):
    """External data providers for lead discovery."""

    HACKER_NEWS = "hacker_news"
    REMOTIVE = "remotive"


class LeadStatus(StrEnum):
    """Lead lifecycle state machine."""

    NEW = "new"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    CONTACTED = "contacted"
    ARCHIVED = "archived"


class SkillMatchResult(BaseModel):
    """
    Scoring outcome produced by the matching engine.
    Pattern: Value Object (Immutable).
    """

    model_config = ConfigDict(frozen=True)

    score: int = Field(..., ge=0, le=100, description="Relevance score (0-100)")
    matched_skills: list[str] = Field(default_factory=list, description="Matched target keywords")
    is_qualified: bool = Field(default=False, description="True if score meets threshold")


class RawLead(BaseModel):
    """
    Canonical normalized lead from discovery providers.
    Pattern: Value Object (Immutable).
    """

    model_config = ConfigDict(frozen=True, extra="ignore")

    company_name: str = Field(..., description="Canonical name of hiring company")
    title: str = Field(..., description="Role headline or position title")
    description: str = Field(..., description="Sanitized plain-text opportunity description")
    source: LeadSource = Field(..., description="Origin provider")
    source_url: str = Field(..., description="Direct permalink or reference URL")
    source_id: str = Field(..., description="Provider unique ID")
    location: str | None = Field(default=None, description="Extracted geographic location")
    is_remote: bool = Field(default=False, description="Remote work support flag")
    salary_info: str | None = Field(default=None, description="Extracted compensation details")
    skills_raw: list[str] = Field(default_factory=list, description="Raw provider tags")
    posted_at: datetime | None = Field(default=None, description="Original publication timestamp")
    discovered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC ingestion timestamp",
    )
    raw_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific audit metadata",
    )

    @field_validator("company_name", "title", "description", mode="before")
    @classmethod
    def strip_and_validate_text(cls, value: Any) -> str:
        """Enforces clean string boundaries."""
        if not isinstance(value, str):
            value = str(value) if value is not None else ""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or solely whitespace.")
        return cleaned


class Lead(BaseModel):
    """
    Core Domain Entity representing a discovered, scored opportunity.
    Pattern: DDD Entity (Identified by UUID).
    """

    model_config = ConfigDict(extra="ignore")

    id: UUID = Field(default_factory=uuid4, description="Unique lead identifier")
    company_name: str = Field(..., description="Hiring company name")
    title: str = Field(..., description="Role headline")
    description: str = Field(..., description="Opportunity description")
    source: LeadSource = Field(..., description="Discovery source")
    source_url: str = Field(..., description="Reference URL")
    source_id: str = Field(..., description="Provider unique identifier")
    location: str | None = Field(default=None, description="Geographic location")
    is_remote: bool = Field(default=False, description="Remote work flag")
    salary_info: str | None = Field(default=None, description="Compensation information")
    match_score: int = Field(default=0, ge=0, le=100, description="Skill relevance score")
    matched_skills: list[str] = Field(default_factory=list, description="Matched skills list")
    status: LeadStatus = Field(default=LeadStatus.NEW, description="Current lifecycle status")
    posted_at: datetime | None = Field(default=None, description="Original posting time")
    discovered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Ingestion timestamp",
    )
    raw_metadata: dict[str, Any] = Field(default_factory=dict, description="Audit metadata")
    created_at: datetime | None = Field(default=None, description="Persistence creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Persistence update timestamp")

    @classmethod
    def from_raw_lead(
        cls,
        raw_lead: RawLead,
        match_result: SkillMatchResult | None = None,
    ) -> "Lead":
        """
        Factory Method: Creates a Lead entity from a RawLead and optional scoring result.
        """
        score = match_result.score if match_result else 0
        matched = match_result.matched_skills if match_result else []
        status = (
            LeadStatus.QUALIFIED
            if (match_result and match_result.is_qualified)
            else (LeadStatus.DISQUALIFIED if match_result else LeadStatus.NEW)
        )

        return cls(
            company_name=raw_lead.company_name,
            title=raw_lead.title,
            description=raw_lead.description,
            source=raw_lead.source,
            source_url=raw_lead.source_url,
            source_id=raw_lead.source_id,
            location=raw_lead.location,
            is_remote=raw_lead.is_remote,
            salary_info=raw_lead.salary_info,
            match_score=score,
            matched_skills=matched,
            status=status,
            posted_at=raw_lead.posted_at,
            discovered_at=raw_lead.discovered_at,
            raw_metadata=raw_lead.raw_metadata,
        )


    def to_raw_lead(self) -> RawLead:
        """
        Converts Lead domain entity back into a canonical RawLead for deduplication index matching.
        Design Pattern: Data Mapper / Adapter
        """
        return RawLead(
            company_name=self.company_name,
            title=self.title,
            description=self.description,
            source=self.source,
            source_url=self.source_url,
            source_id=self.source_id,
            location=self.location,
            is_remote=self.is_remote,
            salary_info=self.salary_info,
            skills_raw=self.matched_skills,
            posted_at=self.posted_at,
            discovered_at=self.discovered_at,
            raw_metadata=self.raw_metadata,
        )
