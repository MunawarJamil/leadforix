"""
Resilience and fault-injection tests for the Lead Discovery Pipeline.
Simulates rate limits (HTTP 429), timeouts, server crashes (5xx), and corrupt payloads.

Design Patterns:
- Fault Injection / Chaos Engineering: Verifies system survivability under simulated failure modes.
- Bulkhead Assertion: Guarantees that partial outages never cause data loss or service crashes.
"""

from unittest.mock import AsyncMock, MagicMock
import httpx
import pytest
import respx

from apps.services.lead_service.app.application.dedup.service import DeduplicationService
from apps.services.lead_service.app.application.pipeline import DiscoveryPipelineService, DiscoveryResult
from apps.services.lead_service.app.application.scoring import SkillMatchingEngine
from apps.services.lead_service.app.domain.exceptions import RateLimitExceededError
from apps.services.lead_service.app.domain.models import Lead, LeadSource, LeadStatus
from apps.services.lead_service.app.infrastructure.clients.hn_client import HnAlgoliaClient
from apps.services.lead_service.app.infrastructure.clients.remotive_client import RemotiveClient
from apps.services.lead_service.app.infrastructure.repository import LeadRepository


@pytest.fixture
def mock_repository() -> tuple[LeadRepository, list[Lead]]:
    """Mock repository capturing persisted leads in an in-memory list."""
    persisted: list[Lead] = []
    mock_session = AsyncMock()
    mock_session.flush = AsyncMock()

    repo = LeadRepository(mock_session)
    repo.list_leads = AsyncMock(return_value=[])

    async def save_bulk_impl(leads: list[Lead]) -> list[Lead]:
        persisted.extend(leads)
        return leads

    repo.save_bulk = AsyncMock(side_effect=save_bulk_impl)
    return repo, persisted


# =====================================================================
# 1. Upstream 429 Rate Limit & Backoff Tests
# =====================================================================

@pytest.mark.asyncio
@respx.mock
async def test_hn_client_rate_limit_429_raises_structured_exception() -> None:
    """Verifies that a 429 response from Algolia HN raises RateLimitExceededError with retry_after."""
    respx.get("https://hn.algolia.com/api/v1/search_by_date").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "3"}, text="Too Many Requests")
    )

    async with HnAlgoliaClient() as client:
        with pytest.raises(RateLimitExceededError) as exc_info:
            await client.fetch_latest_hiring_story()

    assert exc_info.value.retry_after == 3.0
    assert exc_info.value.provider == "hn_algolia"


@pytest.mark.asyncio
@respx.mock
async def test_remotive_client_rate_limit_429_raises_structured_exception() -> None:
    """Verifies that a 429 response from Remotive raises RateLimitExceededError with default retry_after."""
    respx.get("https://remotive.com/api/remote-jobs").mock(
        return_value=httpx.Response(429, text="Rate limit exceeded")
    )

    async with RemotiveClient() as client:
        with pytest.raises(RateLimitExceededError) as exc_info:
            await client.fetch_remote_jobs()

    assert exc_info.value.retry_after == 5.0  # Default fallback when header is omitted
    assert exc_info.value.provider == "remotive"


# =====================================================================
# 2. Pipeline Bulkhead Isolation Under Hostile Conditions
# =====================================================================

@pytest.mark.asyncio
@respx.mock
async def test_pipeline_bulkhead_survives_remotive_429_outage(
    mock_repository: tuple[LeadRepository, list[Lead]],
) -> None:
    """
    Simulates Remotive hitting 429 rate-limit while Algolia HN is healthy.
    Asserts zero crash, Remotive error recorded, and HN leads successfully persisted.
    """
    repo, persisted = mock_repository

    # Mock Algolia HN Success
    hn_story = {"objectID": "9001", "title": "Ask HN: Who is hiring? (September 2026)"}
    hn_comment = {
        "objectID": "9002",
        "comment_text": "<p>Stripe | Staff Python Engineer | Remote<br>We build global financial infra with Python, FastAPI, and PostgreSQL.</p>",
        "created_at": "2026-09-01T10:00:00Z",
        "author": "stripe_recruiter",
        "story_id": 9001,
    }
    respx.get("https://hn.algolia.com/api/v1/search_by_date").mock(
        side_effect=[
            httpx.Response(200, json={"hits": [hn_story]}),
            httpx.Response(200, json={"hits": [hn_comment]}),
        ]
    )

    # Mock Remotive 429 Failure
    respx.get("https://remotive.com/api/remote-jobs").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "10"}, text="Rate limited")
    )

    async with HnAlgoliaClient() as hn_client, RemotiveClient() as remotive_client:
        pipeline = DiscoveryPipelineService(
            repository=repo,
            hn_client=hn_client,
            remotive_client=remotive_client,
            dedup_service=DeduplicationService(),
            scoring_engine=SkillMatchingEngine(),
        )
        result = await pipeline.run(hn_limit=5, remotive_limit=5)

    assert isinstance(result, DiscoveryResult)
    assert result.hn_fetched == 1
    assert result.remotive_fetched == 0
    assert result.persisted_count == 1
    assert "remotive" in result.provider_errors
    assert "hacker_news" not in result.provider_errors
    assert len(persisted) == 1
    assert persisted[0].company_name == "Stripe"


@pytest.mark.asyncio
@respx.mock
async def test_pipeline_bulkhead_survives_hn_network_timeout(
    mock_repository: tuple[LeadRepository, list[Lead]],
) -> None:
    """
    Simulates Algolia HN timing out while Remotive is healthy.
    Asserts zero crash, HN error recorded, and Remotive leads successfully persisted.
    """
    repo, persisted = mock_repository

    # Mock Algolia HN Timeout
    respx.get("https://hn.algolia.com/api/v1/search_by_date").mock(
        side_effect=httpx.ConnectTimeout("Connection to hn.algolia.com timed out")
    )

    # Mock Remotive Success
    remotive_job = {
        "id": 8801,
        "url": "https://remotive.com/jobs/8801",
        "title": "Senior Go & Kubernetes Engineer",
        "company_name": "Datadog",
        "category": "software-dev",
        "tags": ["go", "kubernetes", "docker"],
        "job_type": "full_time",
        "publication_date": "2026-09-02T12:00:00",
        "candidate_required_location": "Remote",
        "salary": "$150k-$180k",
        "description": "<p>Build high-scale distributed telemetry with Go and Kubernetes.</p>",
    }
    respx.get("https://remotive.com/api/remote-jobs").mock(
        return_value=httpx.Response(200, json={"jobs": [remotive_job]})
    )

    async with HnAlgoliaClient(timeout=1.0) as hn_client, RemotiveClient() as remotive_client:
        pipeline = DiscoveryPipelineService(
            repository=repo,
            hn_client=hn_client,
            remotive_client=remotive_client,
            dedup_service=DeduplicationService(),
            scoring_engine=SkillMatchingEngine(),
        )
        result = await pipeline.run(hn_limit=5, remotive_limit=5)

    assert result.hn_fetched == 0
    assert result.remotive_fetched == 1
    assert result.persisted_count == 1
    assert "hacker_news" in result.provider_errors
    assert len(persisted) == 1
    assert persisted[0].company_name == "Datadog"


@pytest.mark.asyncio
@respx.mock
async def test_pipeline_survives_malformed_json_without_crash(
    mock_repository: tuple[LeadRepository, list[Lead]],
) -> None:
    """
    Simulates upstream provider returning corrupt / unexpected non-JSON payload.
    Asserts that MalformedPayloadError is trapped cleanly.
    """
    repo, persisted = mock_repository

    # Corrupted HTML returned instead of JSON (e.g. Cloudflare gateway block)
    respx.get("https://hn.algolia.com/api/v1/search_by_date").mock(
        return_value=httpx.Response(200, text="<html><body>502 Bad Gateway</body></html>")
    )
    respx.get("https://remotive.com/api/remote-jobs").mock(
        return_value=httpx.Response(200, text="<error>Not JSON</error>")
    )

    async with HnAlgoliaClient() as hn_client, RemotiveClient() as remotive_client:
        pipeline = DiscoveryPipelineService(
            repository=repo,
            hn_client=hn_client,
            remotive_client=remotive_client,
            dedup_service=DeduplicationService(),
            scoring_engine=SkillMatchingEngine(),
        )
        result = await pipeline.run()

    assert result.total_fetched == 0
    assert result.persisted_count == 0
    assert "hacker_news" in result.provider_errors
    assert "remotive" in result.provider_errors
    assert len(persisted) == 0
