"""
Parser for Hacker News 'Who is hiring?' comment threads.

Design Pattern: Adapter / Heuristic Parser
- Transforms semi-structured community comments into canonical RawLead Value Objects.
- Uses regex and delimiter heuristics to extract company, position, remote status,
  location, and compensation.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any

from apps.services.lead_service.app.application.sanitizer import (
    clean_html_to_text,
    normalize_company_name,
)
from apps.services.lead_service.app.domain.models import LeadSource, RawLead
from apps.services.lead_service.app.infrastructure.clients.schemas import HnCommentHit

logger = logging.getLogger("lead_service.parsers.hn")

# Common patterns in HN hiring headers
_REMOTE_REGEX = re.compile(r"\b(?:remote|anywhere|distributed|worldwide)\b", re.IGNORECASE)
_SALARY_REGEX = re.compile(
    r"(?:\$|€|£)\s*\d+(?:[.,]\d+)?\s*(?:k|K|m|M)?(?:\s*(?:-|to)\s*(?:\$|€|£)?\s*\d+(?:[.,]\d+)?\s*(?:k|K|m|M)?)?",
    re.IGNORECASE,
)
_YC_BATCH_REGEX = re.compile(r"\(YC\s*[WSF]?\d+\)", re.IGNORECASE)


class HnCommentParser:
    """
    Heuristic parser for extracting structured hiring opportunities from Hacker News comments.
    """

    HN_ITEM_BASE_URL = "https://news.ycombinator.com/item?id="

    @classmethod
    def parse_comment(cls, hit: HnCommentHit) -> RawLead | None:
        """
        Parses a single HN comment into a validated RawLead.
        Returns None if the comment is deleted, a non-hiring discussion, or unparseable.
        """
        if not hit.comment_text or hit.comment_text.strip() in ("[deleted]", "[dead]"):
            return None

        # Clean HTML tags and decode entities
        clean_text = clean_html_to_text(hit.comment_text)
        if not clean_text or len(clean_text) < 30:
            return None

        # Split into header line and remaining description body
        paragraphs = clean_text.split("\n\n", 1)
        header_line = paragraphs[0].strip().split("\n")[0]
        body = paragraphs[1].strip() if len(paragraphs) > 1 else clean_text

        # Extract metadata from header line using standard delimiters
        parsed_header = cls._parse_header_line(header_line)
        if not parsed_header:
            return None

        company_raw, role_raw, location_raw, is_remote_header = parsed_header

        # Clean company name (remove YC tags, extra spaces)
        company_name = _YC_BATCH_REGEX.sub("", company_raw).strip(" -|:")
        if not company_name:
            return None

        title = role_raw.strip(" -|:") if role_raw else "Software Engineer"

        # Check for remote signals across header and full text
        is_remote = is_remote_header or bool(_REMOTE_REGEX.search(header_line))

        # Extract compensation if mentioned
        salary_match = _SALARY_REGEX.search(clean_text)
        salary_info = salary_match.group(0).strip() if salary_match else None

        # Parse publication timestamp
        posted_at = cls._parse_timestamp(hit.created_at)

        try:
            return RawLead(
                company_name=company_name,
                title=title,
                description=clean_text,
                source=LeadSource.HACKER_NEWS,
                source_url=f"{cls.HN_ITEM_BASE_URL}{hit.objectID}",
                source_id=hit.objectID,
                location=location_raw,
                is_remote=is_remote,
                salary_info=salary_info,
                skills_raw=[],
                posted_at=posted_at,
                raw_metadata={
                    "author": hit.author,
                    "story_id": hit.story_id,
                    "parent_id": hit.parent_id,
                },
            )
        except Exception as exc:
            logger.debug("Skipping HN comment id=%s: %s", hit.objectID, exc)
            return None

    @classmethod
    def _parse_header_line(
        cls, header: str
    ) -> tuple[str, str, str | None, bool] | None:
        """
        Extracts (company, role, location, is_remote) from delimiter-separated headers.

        Supports:
        - Pipe delimited: "Company | Role | Location | Remote"
        - Dash delimited: "Company - Role - Location - Remote"
        """
        tokens: list[str] = []
        if "|" in header:
            tokens = [t.strip() for t in header.split("|") if t.strip()]
        elif " - " in header:
            tokens = [t.strip() for t in header.split(" - ") if t.strip()]

        if not tokens or len(tokens) < 2:
            return None

        company = tokens[0]
        role = tokens[1]
        location: str | None = None
        is_remote = False

        # Inspect remaining tokens for location and remote flags
        if len(tokens) > 2:
            remaining = tokens[2:]
            for token in remaining:
                if _REMOTE_REGEX.search(token):
                    is_remote = True
                elif not location and len(token) < 50:
                    location = token

        return company, role, location, is_remote

    @staticmethod
    def _parse_timestamp(date_str: str | None) -> datetime | None:
        """Safely parses ISO timestamps from Algolia."""
        if not date_str:
            return None
        try:
            normalized = date_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None

    @classmethod
    def parse_many(cls, hits: list[HnCommentHit]) -> list[RawLead]:
        """Parses a batch of HN comment hits, filtering out unparseable items."""
        leads: list[RawLead] = []
        for hit in hits:
            lead = cls.parse_comment(hit)
            if lead:
                leads.append(lead)
        return leads
