"""
Discovery pipeline application service orchestrating ingestion, normalization,
deduplication, skill-scoring, and persistence.

Design Patterns:
- Service Layer: Coordinates multi-provider ingestion workflow without coupling to transports.
- Dependency Injection: Receives API clients, scoring engine, dedup service, and repository.
- Fault Isolation / Bulkhead: Isolates upstream provider failures so one provider outage
  does not break the entire discovery cycle.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import time
from typing import Any

from apps.services.lead_service.app.application.dedup.service import DedupService
from apps.services.lead_service.app.application.mappers.remotive_mapper import RemotiveMapper
from apps.services.lead_service.app.application.parsers.hn_parser import HnCommentParser
from apps.services.lead_service.app.application.scoring import SkillConfig, SkillMatchingEngine
from apps.services.lead_service.app.domain.models import Lead, LeadSource, RawLead
from apps.services.lead_service.app.infrastructure.clients.hn_client import HnAlgoliaClient
from apps.services.lead_service.app.infrastructure.clients.remotive_client import RemotiveClient
from apps.services.lead_service.app.infrastructure.repository import LeadRepository

logger = logging.getLogger("lead_service.pipeline")


@dataclass(frozen=True)
class DiscoveryResult:
    """
    Summary execution telemetry returned by the discovery pipeline.
    Pattern: Value Object.
    """

    total_fetched: int
    hn_fetched: int
    remotive_fetched: int
    duplicates_dropped: int
    total_unique: int
    qualified_count: int
    disqualified_count: int
    persisted_count: int
    duration_seconds: float
    started_at: datetime
    completed_at: datetime
    provider_errors: dict[str, str] = field(default_factory=dict)


class DiscoveryPipelineService:
    """
    Application orchestrator for multi-source public hiring discovery.
    Pattern: Orchestrator / Service Layer.
    """

    def __init__(
        self,
        repository: LeadRepository,
        hn_client: HnAlgoliaClient | None = None,
        remotive_client: RemotiveClient | None = None,
        dedup_service: DedupService | None = None,
        scoring_engine: SkillMatchingEngine | None = None,
    ) -> None:
        self._repository = repository
        self._hn_client = hn_client or HnAlgoliaClient()
        self._remotive_client = remotive_client or RemotiveClient()
        self._dedup_service = dedup_service or DedupService()
        self._scoring_engine = scoring_engine or SkillMatchingEngine()

    async def run(
        self,
        hn_limit: int = 100,
        remotive_limit: int | None = 100,
        remotive_category: str = "software-dev",
        save_only_qualified: bool = False,
    ) -> DiscoveryResult:
        """
        Executes end-to-end discovery run with partial-failure resilience.
        """
        start_time = time.monotonic()
        started_at = datetime.now(timezone.utc)
        provider_errors: dict[str, str] = {}

        logger.info(
            "Starting discovery pipeline execution",
            extra={"hn_limit": hn_limit, "remotive_limit": remotive_limit},
        )

        # Step 1: Parallel upstream fetch with Bulkhead isolation
        hn_task = self._fetch_hacker_news(limit=hn_limit)
        remotive_task = self._fetch_remotive(category=remotive_category, limit=remotive_limit)

        fetch_results = await asyncio.gather(hn_task, remotive_task, return_exceptions=True)

        hn_leads: list[RawLead] = []
        remotive_leads: list[RawLead] = []

        if isinstance(fetch_results[0], Exception):
            err_msg = str(fetch_results[0])
            logger.error("Hacker News ingestion failed: %s", err_msg, exc_info=fetch_results[0])
            provider_errors["hacker_news"] = err_msg
        else:
            hn_leads = fetch_results[0]

        if isinstance(fetch_results[1], Exception):
            err_msg = str(fetch_results[1])
            logger.error("Remotive ingestion failed: %s", err_msg, exc_info=fetch_results[1])
            provider_errors["remotive"] = err_msg
        else:
            remotive_leads = fetch_results[1]

        candidates = hn_leads + remotive_leads
        total_fetched = len(candidates)
        hn_fetched = len(hn_leads)
        remotive_fetched = len(remotive_leads)

        logger.info(
            "Upstream fetch completed",
            extra={
                "total_fetched": total_fetched,
                "hn_fetched": hn_fetched,
                "remotive_fetched": remotive_fetched,
                "errors": list(provider_errors.keys()),
            },
        )

        if not candidates:
            completed_at = datetime.now(timezone.utc)
            return DiscoveryResult(
                total_fetched=0,
                hn_fetched=0,
                remotive_fetched=0,
                duplicates_dropped=0,
                total_unique=0,
                qualified_count=0,
                disqualified_count=0,
                persisted_count=0,
                duration_seconds=round(time.monotonic() - start_time, 3),
                started_at=started_at,
                completed_at=completed_at,
                provider_errors=provider_errors,
            )

        # Step 2: Load historical leads for deduplication
        existing_models = await self._repository.list_leads(limit=1000)
        existing_history = [lead.to_raw_lead() for lead in existing_models]

        # Step 3: Dual-layer deduplication (exact hash + trigram fuzzy)
        unique_raw_leads = self._dedup_service.filter_batch(
            candidates=candidates,
            existing_history=existing_history,
        )
        duplicates_dropped = total_fetched - len(unique_raw_leads)

        # Step 4: Scoring & Entity instantiation
        qualified_leads: list[Lead] = []
        disqualified_leads: list[Lead] = []

        for raw in unique_raw_leads:
            match_res = self._scoring_engine.evaluate(raw)
            lead_entity = Lead.from_raw_lead(raw_lead=raw, match_result=match_res)
            if match_res.is_qualified:
                qualified_leads.append(lead_entity)
            else:
                disqualified_leads.append(lead_entity)

        leads_to_persist = (
            qualified_leads if save_only_qualified else (qualified_leads + disqualified_leads)
        )

        # Step 5: Batch persistence
        persisted_leads = await self._repository.save_bulk(leads_to_persist)
        persisted_count = len(persisted_leads)

        duration = round(time.monotonic() - start_time, 3)
        completed_at = datetime.now(timezone.utc)

        logger.info(
            "Discovery pipeline execution completed",
            extra={
                "persisted_count": persisted_count,
                "qualified": len(qualified_leads),
                "disqualified": len(disqualified_leads),
                "duplicates_dropped": duplicates_dropped,
                "duration_seconds": duration,
            },
        )

        return DiscoveryResult(
            total_fetched=total_fetched,
            hn_fetched=hn_fetched,
            remotive_fetched=remotive_fetched,
            duplicates_dropped=duplicates_dropped,
            total_unique=len(unique_raw_leads),
            qualified_count=len(qualified_leads),
            disqualified_count=len(disqualified_leads),
            persisted_count=persisted_count,
            duration_seconds=duration,
            started_at=started_at,
            completed_at=completed_at,
            provider_errors=provider_errors,
        )

    async def _fetch_hacker_news(self, limit: int) -> list[RawLead]:
        """Fetches and parses top-level HN Who is hiring comments."""
        _, comments = await self._hn_client.fetch_hn_hiring_thread(limit=limit)
        return HnCommentParser.parse_many(comments)

    async def _fetch_remotive(self, category: str, limit: int | None) -> list[RawLead]:
        """Fetches and maps remote jobs from Remotive API."""
        jobs = await self._remotive_client.fetch_remote_jobs(category=category, limit=limit)
        return RemotiveMapper.map_many(jobs)
