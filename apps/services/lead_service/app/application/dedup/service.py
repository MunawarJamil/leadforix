"""
High-performance composite deduplication service for discovered leads.

Design Patterns & Architectural Features:
- Service Layer / Policy Pattern: Encapsulates multi-tier deduplication rules.
- Inverted Trigram Index (Blocking): Replaces O(N^2) pairwise comparisons with
  inverted trigram shingle lookups, pruning disjoint companies in O(1).
- Composite Similarity (Company + Role): Prevents dropping distinct job openings
  at the same company (e.g., Stripe Backend vs Stripe Designer).
- Canonical URL & Source Hash Lookups: O(1) instantaneous exact matching.
- Time-Window Gating: Distinguishes fresh hiring cycles from historical postings.
- Pre-computed Trigram Cache: Eliminates repeated string decomposition in hot loops.
- Structured Reason Codes: Transparent auditing of why leads are accepted or dropped.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import logging

from apps.services.lead_service.app.application.dedup.trigram import (
    generate_trigrams,
    set_jaccard_similarity,
)
from apps.services.lead_service.app.application.sanitizer import (
    normalize_company_name,
    normalize_role_title,
    normalize_url,
)
from apps.services.lead_service.app.domain.models import LeadSource, RawLead

logger = logging.getLogger("lead_service.dedup")

# Default thresholds calibrated for high-precision hiring signal deduplication
DEFAULT_COMPANY_SIMILARITY_THRESHOLD = 0.80
DEFAULT_ROLE_SIMILARITY_THRESHOLD = 0.70
DEFAULT_TIME_WINDOW_DAYS = 60


class DedupReason(StrEnum):
    """Reason code identifying how a duplicate was detected."""

    EXACT_SOURCE_ID = "exact_source_id"
    EXACT_URL = "exact_url"
    FUZZY_COMPOSITE = "fuzzy_composite"


@dataclass(frozen=True)
class DedupMatchResult:
    """
    Detailed match evaluation result for auditing and downstream decisions.
    """

    is_duplicate: bool
    reason: DedupReason | None = None
    matched_lead: RawLead | None = None
    company_similarity: float = 0.0
    role_similarity: float = 0.0


@dataclass(slots=True)
class _CachedLeadRecord:
    """Internal cache entry storing pre-computed normalizations and trigram sets."""

    lead: RawLead
    norm_url: str
    norm_company: str
    company_trigrams: set[str]
    norm_role: str
    role_trigrams: set[str]
    posted_at: datetime | None


class LeadDedupIndex:
    """
    In-memory index supporting O(1) exact lookups and inverted-trigram candidate blocking.
    Reduces comparison complexity from O(N^2) to near O(N) by only testing candidates
    that share character trigrams with known companies.
    """

    def __init__(self) -> None:
        self.source_id_index: dict[tuple[LeadSource, str], RawLead] = {}
        self.url_index: dict[str, RawLead] = {}
        self.records: list[_CachedLeadRecord] = []
        # Inverted index: trigram -> set of indices into self.records
        self.trigram_to_record_indices: dict[str, set[int]] = {}

    def add(self, lead: RawLead) -> None:
        """Indexes a lead across hash lookups and the inverted trigram index."""
        norm_url = normalize_url(lead.source_url)
        norm_company = normalize_company_name(lead.company_name)
        norm_role = normalize_role_title(lead.title)

        company_trigrams = generate_trigrams(norm_company)
        role_trigrams = generate_trigrams(norm_role)

        record_idx = len(self.records)
        record = _CachedLeadRecord(
            lead=lead,
            norm_url=norm_url,
            norm_company=norm_company,
            company_trigrams=company_trigrams,
            norm_role=norm_role,
            role_trigrams=role_trigrams,
            posted_at=lead.posted_at,
        )
        self.records.append(record)

        # 1. Exact Source ID Index
        self.source_id_index[(lead.source, lead.source_id)] = lead

        # 2. Exact Normalized URL Index
        if norm_url:
            self.url_index[norm_url] = lead

        # 3. Inverted Trigram Index for company blocking
        for trigram in company_trigrams:
            if trigram not in self.trigram_to_record_indices:
                self.trigram_to_record_indices[trigram] = set()
            self.trigram_to_record_indices[trigram].add(record_idx)

    def get_candidate_indices_for_trigrams(self, trigrams: set[str]) -> set[int]:
        """Returns record indices that share at least one trigram with the query set."""
        candidate_indices: set[int] = set()
        for trigram in trigrams:
            indices = self.trigram_to_record_indices.get(trigram)
            if indices:
                candidate_indices.update(indices)
        return candidate_indices


class DeduplicationService:
    """
    Production-grade deduplication service combining exact lookups,
    time-window policy, and composite (company + role) fuzzy matching.
    """

    def __init__(
        self,
        company_threshold: float = DEFAULT_COMPANY_SIMILARITY_THRESHOLD,
        role_threshold: float = DEFAULT_ROLE_SIMILARITY_THRESHOLD,
        time_window_days: int | None = DEFAULT_TIME_WINDOW_DAYS,
        similarity_threshold: float | None = None,  # Backwards compatibility alias
    ) -> None:
        if similarity_threshold is not None:
            company_threshold = similarity_threshold

        if not (0.0 < company_threshold <= 1.0):
            raise ValueError(f"company_threshold must be in (0, 1], got {company_threshold}")
        if not (0.0 < role_threshold <= 1.0):
            raise ValueError(f"role_threshold must be in (0, 1], got {role_threshold}")
        if time_window_days is not None and time_window_days < 0:
            raise ValueError("time_window_days must be non-negative")

        self.company_threshold = company_threshold
        self.role_threshold = role_threshold
        self.time_window_days = time_window_days

    def evaluate_candidate(
        self, candidate: RawLead, index: LeadDedupIndex
    ) -> DedupMatchResult:
        """
        Evaluates a candidate against an existing LeadDedupIndex.
        Returns a rich DedupMatchResult with structured reason codes.
        """
        # Tier 1: Exact Source Identity Match (O(1))
        exact_source_match = index.source_id_index.get((candidate.source, candidate.source_id))
        if exact_source_match:
            return DedupMatchResult(
                is_duplicate=True,
                reason=DedupReason.EXACT_SOURCE_ID,
                matched_lead=exact_source_match,
                company_similarity=1.0,
                role_similarity=1.0,
            )

        # Tier 2: Canonical Normalized URL Match (O(1))
        norm_url = normalize_url(candidate.source_url)
        if norm_url:
            exact_url_match = index.url_index.get(norm_url)
            if exact_url_match:
                return DedupMatchResult(
                    is_duplicate=True,
                    reason=DedupReason.EXACT_URL,
                    matched_lead=exact_url_match,
                    company_similarity=1.0,
                    role_similarity=1.0,
                )

        # Tier 3: Inverted Trigram Candidate Blocking
        candidate_norm_comp = normalize_company_name(candidate.company_name)
        if not candidate_norm_comp:
            return DedupMatchResult(is_duplicate=False)

        candidate_comp_trigrams = generate_trigrams(candidate_norm_comp)
        if not candidate_comp_trigrams:
            return DedupMatchResult(is_duplicate=False)

        candidate_record_indices = index.get_candidate_indices_for_trigrams(
            candidate_comp_trigrams
        )
        if not candidate_record_indices:
            # Completely disjoint company: zero shared trigrams, no match possible
            return DedupMatchResult(is_duplicate=False)

        candidate_norm_role = normalize_role_title(candidate.title)
        candidate_role_trigrams = generate_trigrams(candidate_norm_role)

        # Tier 4: Evaluate Pruned Candidates
        for idx in candidate_record_indices:
            cached = index.records[idx]

            # 4a. Time-Window Gating
            if (
                self.time_window_days is not None
                and candidate.posted_at is not None
                and cached.posted_at is not None
            ):
                day_delta = abs((candidate.posted_at - cached.posted_at).total_seconds()) / 86400.0
                if day_delta > self.time_window_days:
                    # Posting belongs to a different hiring season/cycle
                    continue

            # 4b. Company Trigram Similarity
            comp_score = set_jaccard_similarity(candidate_comp_trigrams, cached.company_trigrams)
            if comp_score < self.company_threshold:
                continue

            # 4c. Composite Role Similarity Check
            # Even if company matches, different positions (e.g. Designer vs Backend) are kept!
            role_score = 0.0
            if candidate_norm_role == cached.norm_role:
                role_score = 1.0
            elif candidate_role_trigrams and cached.role_trigrams:
                role_score = set_jaccard_similarity(candidate_role_trigrams, cached.role_trigrams)

            if role_score >= self.role_threshold:
                logger.debug(
                    "Duplicate detected (%s, comp=%.2f, role=%.2f): '%s - %s' matches '%s - %s'",
                    DedupReason.FUZZY_COMPOSITE,
                    comp_score,
                    role_score,
                    candidate.company_name,
                    candidate.title,
                    cached.lead.company_name,
                    cached.lead.title,
                )
                return DedupMatchResult(
                    is_duplicate=True,
                    reason=DedupReason.FUZZY_COMPOSITE,
                    matched_lead=cached.lead,
                    company_similarity=comp_score,
                    role_similarity=role_score,
                )

        return DedupMatchResult(is_duplicate=False)

    def is_duplicate(
        self, candidate: RawLead, existing_leads: Sequence[RawLead]
    ) -> tuple[bool, RawLead | None]:
        """
        Backwards-compatible convenience method.
        Evaluates candidate against a sequence of existing leads.
        """
        index = LeadDedupIndex()
        for lead in existing_leads:
            index.add(lead)

        res = self.evaluate_candidate(candidate, index)
        return res.is_duplicate, res.matched_lead

    def filter_batch(
        self,
        candidates: Sequence[RawLead],
        existing_history: Sequence[RawLead] | None = None,
    ) -> list[RawLead]:
        """
        Filters a stream of candidate leads against historical leads and intra-batch duplicates.
        Operates with O(1) hash index and inverted trigram blocking for optimal scalability.
        """
        index = LeadDedupIndex()
        for lead in (existing_history or []):
            index.add(lead)

        accepted: list[RawLead] = []
        for candidate in candidates:
            match = self.evaluate_candidate(candidate, index)
            if not match.is_duplicate:
                accepted.append(candidate)
                index.add(candidate)  # Add accepted lead to index for subsequent batch items
            else:
                logger.info(
                    "Dropping duplicate lead [%s]: '%s' (%s, %s) matched '%s'",
                    match.reason,
                    candidate.company_name,
                    candidate.title,
                    candidate.source,
                    match.matched_lead.company_name if match.matched_lead else "unknown",
                )

        return accepted
# Alias for backwards compatibility / shorthand
DedupService = DeduplicationService
