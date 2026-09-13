"""
Live end-to-end integration tests for the Lead Discovery Pipeline.
Makes real HTTP calls to the Algolia Hacker News and Remotive APIs.

Design Patterns:
- Realistic Sandbox / E2E Integration: Exercises the live HTTP network layer,
  parsers, deduplication index, and skill scoring engine.
- Spies / In-Memory Sink: Verifies that normalized, scored entities comply with
  persistence schemas and domain rules.
"""

from unittest.mock import AsyncMock, MagicMock
import pytest

from apps.services.lead_service.app.application.dedup.service import DeduplicationService
from apps.services.lead_service.app.application.mappers.remotive_mapper import RemotiveMapper
from apps.services.lead_service.app.application.parsers.hn_parser import HnCommentParser
from apps.services.lead_service.app.application.pipeline import DiscoveryPipelineService, DiscoveryResult
from apps.services.lead_service.app.application.scoring import SkillMatchingEngine
from apps.services.lead_service.app.domain.models import Lead, LeadSource, LeadStatus
from apps.services.lead_service.app.infrastructure.clients.hn_client import HnAlgoliaClient
from apps.services.lead_service.app.infrastructure.clients.remotive_client import RemotiveClient
from apps.services.lead_service.app.infrastructure.repository import LeadRepository


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_algolia_hn_fetch_and_parse() -> None:
    """Queries live Algolia HN Search API and verifies parsing on real comments."""
    async with HnAlgoliaClient(timeout=20.0) as client:
        story, comments = await client.fetch_hn_hiring_thread(limit=15)

    assert story is not None, "Active 'Who is hiring?' story should be found on HN Algolia."
    assert "hiring" in story.title.lower()
    assert len(comments) > 0, "Should retrieve real comments from the hiring thread."

    raw_leads = HnCommentParser.parse_many(comments)
    assert len(raw_leads) > 0, "At least one top-level comment should parse into a valid RawLead."

    sample_lead = raw_leads[0]
    assert sample_lead.company_name
    assert sample_lead.title
    assert sample_lead.source == LeadSource.HACKER_NEWS
    assert sample_lead.source_url.startswith("https://news.ycombinator.com/item?id=")
    assert len(sample_lead.description) > 20


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_remotive_fetch_and_map() -> None:
    """Queries live Remotive API and verifies mapping on real job postings."""
    async with RemotiveClient(timeout=20.0) as client:
        jobs = await client.fetch_remote_jobs(category="software-dev", limit=5)

    assert len(jobs) > 0, "Should retrieve real remote software jobs from Remotive."

    raw_leads = RemotiveMapper.map_many(jobs)
    assert len(raw_leads) > 0, "Should successfully map Remotive items to RawLead entities."

    sample_lead = raw_leads[0]
    assert sample_lead.company_name
    assert sample_lead.title
    assert sample_lead.source == LeadSource.REMOTIVE
    assert sample_lead.is_remote is True
    assert sample_lead.source_url.startswith("http")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_discovery_pipeline_end_to_end() -> None:
    """
    Executes an end-to-end pipeline run against live APIs.
    Verifies that raw leads are fetched, deduplicated, scored, and passed to the repository.
    """
    persisted_leads: list[Lead] = []

    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    mock_session.flush = AsyncMock()

    # Capture persisted leads to assert domain correctness
    async def capture_bulk(leads: list[Lead]) -> list[Lead]:
        persisted_leads.extend(leads)
        return leads

    repo = LeadRepository(mock_session)
    repo.list_leads = AsyncMock(return_value=[])  # Empty initial database
    repo.save_bulk = AsyncMock(side_effect=capture_bulk)

    async with HnAlgoliaClient(timeout=25.0) as hn_client, RemotiveClient(timeout=25.0) as remotive_client:
        pipeline = DiscoveryPipelineService(
            repository=repo,
            hn_client=hn_client,
            remotive_client=remotive_client,
            dedup_service=DeduplicationService(),
            scoring_engine=SkillMatchingEngine(),
        )

        result = await pipeline.run(
            hn_limit=10,
            remotive_limit=10,
            remotive_category="software-dev",
            save_only_qualified=False,
        )

    assert isinstance(result, DiscoveryResult)
    assert result.total_fetched > 0, "Pipeline should fetch opportunities from live APIs."
    assert result.total_unique > 0, "Should produce unique leads after deduplication."
    assert result.persisted_count > 0, "Should persist unique leads."
    assert result.duration_seconds > 0.0
    assert result.provider_errors == {}, f"Unexpected provider errors: {result.provider_errors}"

    # Verify attributes of real persisted leads
    assert len(persisted_leads) == result.persisted_count
    for lead in persisted_leads:
        assert lead.id is not None
        assert lead.company_name
        assert lead.title
        assert lead.source in (LeadSource.HACKER_NEWS, LeadSource.REMOTIVE)
        assert 0 <= lead.match_score <= 100
        assert lead.status in (LeadStatus.QUALIFIED, LeadStatus.DISQUALIFIED)
        if lead.status == LeadStatus.QUALIFIED:
            assert lead.match_score >= 40
            assert len(lead.matched_skills) > 0
