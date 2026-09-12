"""
Deduplication service for discovered leads.

Design Patterns:
- Service Layer / Policy Pattern: Encapsulates deduplication rules and similarity thresholds.
- Pipeline Filter: Filters candidate streams against seen history and within-batch duplicates.
"""

from collections.abc import Sequence
import logging

from apps.services.lead_service.app.application.dedup.trigram import (
    trigram_similarity,
)
from apps.services.lead_service.app.application.sanitizer import (
    normalize_company_name,
)
from apps.services.lead_service.app.domain.models import RawLead

logger = logging.getLogger("lead_service.dedup")

# Default similarity threshold matching pg_trgm standard recommendation
DEFAULT_SIMILARITY_THRESHOLD = 0.85


class DeduplicationService:
    """
    Evaluates new RawLead candidates against existing leads or batch items
    to prevent duplicate lead creation.
    """

    def __init__(self, similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> None:
        self.similarity_threshold = similarity_threshold

    def is_duplicate(
        self, candidate: RawLead, existing_leads: Sequence[RawLead]
    ) -> tuple[bool, RawLead | None]:
        """
        Determines if a candidate matches any lead in existing_leads.

        Returns:
            (is_duplicate: bool, matched_lead: RawLead | None)
        """
        candidate_norm_name = normalize_company_name(candidate.company_name)

        for existing in existing_leads:
            # 1. Exact Source Identity Match (same provider and same item ID)
            if (
                candidate.source == existing.source
                and candidate.source_id == existing.source_id
            ):
                return True, existing

            # 2. Exact URL Match (same destination posting)
            if candidate.source_url == existing.source_url:
                return True, existing

            # 3. Fuzzy Company Name Match
            existing_norm_name = normalize_company_name(existing.company_name)
            if candidate_norm_name and existing_norm_name:
                score = trigram_similarity(candidate_norm_name, existing_norm_name)
                if score >= self.similarity_threshold:
                    logger.debug(
                        "Fuzzy duplicate found (score=%.2f): '%s' matches '%s'",
                        score,
                        candidate.company_name,
                        existing.company_name,
                    )
                    return True, existing

        return False, None

    def filter_batch(
        self,
        candidates: Sequence[RawLead],
        existing_history: Sequence[RawLead] | None = None,
    ) -> list[RawLead]:
        """
        Filters a candidate batch, eliminating:
        1. Candidates matching historical leads in `existing_history`.
        2. Intra-batch duplicates (earlier candidates take precedence).
        """
        accepted: list[RawLead] = []
        comparison_pool = list(existing_history or [])

        for candidate in candidates:
            dup, match = self.is_duplicate(candidate, comparison_pool)
            if not dup:
                accepted.append(candidate)
                comparison_pool.append(candidate)
            else:
                logger.info(
                    "Dropping duplicate lead: '%s' (%s) matched '%s'",
                    candidate.company_name,
                    candidate.source,
                    match.company_name if match else "unknown",
                )

        return accepted
