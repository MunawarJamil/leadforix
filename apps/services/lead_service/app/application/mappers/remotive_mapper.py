"""
Mapper adapter for converting Remotive API job listings into canonical RawLead domain entities.

Design Pattern: Adapter / Mapper
- Adapts third-party DTOs (`RemotiveJobItem`) to domain Value Objects (`RawLead`).
- Isolates Remotive schema quirks and data cleaning from the rest of the application.
"""

from datetime import datetime, timezone
import logging
from typing import Any
from apps.services.lead_service.app.application.sanitizer import clean_html_to_text
from apps.services.lead_service.app.domain.models import LeadSource, RawLead
from apps.services.lead_service.app.infrastructure.clients.schemas import RemotiveJobItem

logger = logging.getLogger("lead_service.mappers.remotive")


class RemotiveMapper:
    """
    Adapter responsible for translating Remotive API jobs into canonical RawLead entities.
    """

    @classmethod
    def to_raw_lead(cls, job: RemotiveJobItem) -> RawLead | None:
        """
        Converts a RemotiveJobItem into a validated, sanitized RawLead.
        Returns None if essential fields are missing or unrecoverable.
        """
        try:
            cleaned_description = clean_html_to_text(job.description)
            if not cleaned_description:
                # Fall back to title if description is completely empty
                cleaned_description = job.title.strip()

            company_name = job.company_name.strip()
            title = job.title.strip()

            if not company_name or not title:
                logger.warning(
                    "Skipping Remotive job id=%s: missing company_name or title",
                    job.id,
                )
                return None

            # Parse publication timestamp safely
            posted_at = cls._parse_timestamp(job.publication_date)

            # Deduplicate and normalize raw tags
            skills_raw: list[str] = []
            seen_skills: set[str] = set()
            for tag in job.tags:
                clean_tag = tag.strip().lower()
                if clean_tag and clean_tag not in seen_skills:
                    seen_skills.add(clean_tag)
                    skills_raw.append(clean_tag)

            if job.category:
                clean_cat = job.category.strip().lower()
                if clean_cat and clean_cat not in seen_skills:
                    skills_raw.append(clean_cat)

            return RawLead(
                company_name=company_name,
                title=title,
                description=cleaned_description,
                source=LeadSource.REMOTIVE,
                source_url=job.url,
                source_id=str(job.id),
                location=job.candidate_required_location or "Remote",
                is_remote=True,  # All Remotive jobs are remote by definition
                salary_info=job.salary.strip() if job.salary else None,
                skills_raw=skills_raw,
                posted_at=posted_at,
                raw_metadata={
                    "job_type": job.job_type,
                    "category": job.category,
                    "company_logo": job.company_logo,
                },
            )

        except Exception as exc:
            logger.error("Failed to map RemotiveJobItem id=%s: %s", job.id, exc)
            return None

    @staticmethod
    def _parse_timestamp(date_str: str | None) -> datetime | None:
        """Safely parses ISO 8601 publication timestamps into UTC datetimes."""
        if not date_str:
            return None
        try:
            # Handle 'Z' suffix in ISO strings for Python <3.11 compatibility
            normalized = date_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None

    @classmethod
    def map_many(cls, jobs: list[RemotiveJobItem]) -> list[RawLead]:
        """Maps a collection of Remotive items, dropping invalid records."""
        leads: list[RawLead] = []
        for job in jobs:
            lead = cls.to_raw_lead(job)
            if lead:
                leads.append(lead)
        return leads
