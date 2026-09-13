"""
SQLAlchemy ORM models for the Lead Discovery persistence subsystem.

Design Patterns:
- Data Mapper Pattern: Maps relational database rows to domain entities.
- Factory Method: `from_domain` and `from_raw_lead` construct ORM instances.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from apps.services.lead_service.app.domain.models import (
    Lead,
    LeadSource,
    LeadStatus,
    RawLead,
    SkillMatchResult,
)
from shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class LeadModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQLAlchemy ORM model representing the 'leads' database table.
    Pattern: Data Mapper.
    """

    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_leads_source_source_id", "source", "source_id", unique=True),
        Index("ix_leads_status_match_score", "status", "match_score"),
    )

    company_name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    source_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    source_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_remote: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    salary_info: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    match_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        index=True,
        nullable=False,
    )
    matched_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=LeadStatus.NEW.value,
        index=True,
        nullable=False,
    )
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    raw_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    def to_domain(self) -> Lead:
        """Translates ORM model to pure domain Lead entity."""
        return Lead(
            id=self.id,
            company_name=self.company_name,
            title=self.title,
            description=self.description,
            source=LeadSource(self.source),
            source_url=self.source_url,
            source_id=self.source_id,
            location=self.location,
            is_remote=self.is_remote,
            salary_info=self.salary_info,
            match_score=self.match_score,
            matched_skills=self.matched_skills,
            status=LeadStatus(self.status),
            posted_at=self.posted_at,
            discovered_at=self.discovered_at,
            raw_metadata=self.raw_metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, lead: Lead) -> "LeadModel":
        """Factory Method creating ORM model from a domain entity."""
        return cls(
            id=lead.id,
            company_name=lead.company_name,
            title=lead.title,
            description=lead.description,
            source=lead.source.value,
            source_url=lead.source_url,
            source_id=lead.source_id,
            location=lead.location,
            is_remote=lead.is_remote,
            salary_info=lead.salary_info,
            match_score=lead.match_score,
            matched_skills=lead.matched_skills,
            status=lead.status.value,
            posted_at=lead.posted_at,
            discovered_at=lead.discovered_at,
            raw_metadata=lead.raw_metadata,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
        )

    @classmethod
    def from_raw_lead(
        cls,
        raw_lead: RawLead,
        match_result: SkillMatchResult | None = None,
    ) -> "LeadModel":
        """Factory Method creating ORM model directly from RawLead and score."""
        domain_lead = Lead.from_raw_lead(raw_lead, match_result)
        return cls.from_domain(domain_lead)
