"""
Mapper adapter for converting Arbeitnow API job listings into canonical RawLead domain entities.

Design Pattern: Adapter / Mapper
- Adapts third-party DTOs (`ArbeitnowJobItem`) to domain Value Objects (`RawLead`).
- Isolates Arbeitnow schema quirks, HTML cleaning, and timestamp normalization.
"""

from datetime import datetime, timezone
import logging

from apps.services.lead_service.app.application.sanitizer import clean_html_to_text
from apps.services.lead_service.app.domain.models import LeadSource, RawLead
from apps.services.lead_service.app.infrastructure.clients.schemas import ArbeitnowJobItem

logger = logging.getLogger("lead_service.mappers.arbeitnow")


class ArbeitnowMapper:
    """
    Adapter responsible for translating Arbeitnow API jobs into canonical RawLead entities.
    """

    @classmethod
    def to_raw_lead(cls, job: ArbeitnowJobItem) -> RawLead | None:
        """
        Converts an ArbeitnowJobItem into a validated, sanitized RawLead.
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
                    "Skipping Arbeitnow job slug=%s: missing company_name or title",
                    job.slug,
                )
                return None

            # Parse publication timestamp safely (epoch seconds -> UTC datetime)
            posted_at = cls._parse_timestamp(job.created_at)

            # Deduplicate and normalize raw tags
            skills_raw: list[str] = []
            seen_skills: set[str] = set()
            for tag in job.tags:
                clean_tag = tag.strip().lower()
                if clean_tag and clean_tag not in seen_skills:
                    seen_skills.add(clean_tag)
                    skills_raw.append(clean_tag)

            # Determine location and remote flag
            is_remote = bool(job.remote)
            location = job.location.strip() if job.location else ("Remote" if is_remote else None)

            return RawLead(
                company_name=company_name,
                title=title,
                description=cleaned_description,
                source=LeadSource.ARBEITNOW,
                source_url=job.url,
                source_id=job.slug,
                location=location,
                is_remote=is_remote,
                salary_info=None,
                skills_raw=skills_raw,
                posted_at=posted_at,
                raw_metadata={
                    "job_types": job.job_types,
                    "slug": job.slug,
                },
            )

        except Exception as exc:
            logger.error("Failed to map ArbeitnowJobItem slug=%s: %s", job.slug, exc)
            return None

    @staticmethod
    def _parse_timestamp(timestamp: int | None) -> datetime | None:
        """Safely parses Unix epoch timestamps (seconds) into UTC datetimes."""
        if not timestamp:
            return None
        try:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return None

    @classmethod
    def map_many(cls, jobs: list[ArbeitnowJobItem]) -> list[RawLead]:
        """Maps a collection of Arbeitnow items, dropping invalid records."""
        leads: list[RawLead] = []
        for job in jobs:
            lead = cls.to_raw_lead(job)
            if lead:
                leads.append(lead)
        return leads
