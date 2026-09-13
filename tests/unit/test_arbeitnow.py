"""
Unit and integration tests for Arbeitnow API Client, Mapper Adapter, and Pipeline Orchestration.

Design Patterns:
- Mock / Test Double: Isolates HTTP network calls via `respx`.
- Fault Injection: Verifies resilient fallback on 429 rate limits, 500 server errors, and timeouts.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx

from apps.services.lead_service.app.application.dedup.service import DedupService
from apps.services.lead_service.app.application.mappers.arbeitnow_mapper import ArbeitnowMapper
from apps.services.lead_service.app.application.pipeline import DiscoveryPipelineService
from apps.services.lead_service.app.application.scoring import SkillMatchingEngine
from apps.services.lead_service.app.domain.exceptions import (
    DiscoveryTimeoutError,
    MalformedPayloadError,
    RateLimitExceededError,
    UpstreamServiceError,
)
from apps.services.lead_service.app.domain.models import LeadSource, RawLead
from apps.services.lead_service.app.infrastructure.clients.arbeitnow_client import ArbeitnowClient
from apps.services.lead_service.app.infrastructure.clients.schemas import (
    ArbeitnowJobItem,
    HnCommentHit,
    RemotiveJobItem,
)

# ---------------------------------------------------------------------------
# Fixtures & Sample Payloads
# ---------------------------------------------------------------------------

SAMPLE_ARBEITNOW_PAYLOAD = {
    "data": [
        {
            "slug": "senior-python-engineer-101",
            "company_name": "Tech Corp",
            "title": "Senior Python Engineer",
            "description": "<p>We are seeking a <b>Senior Python Engineer</b> with FastAPI experience.<br>Remote eligible.</p>",
            "remote": True,
            "url": "https://www.arbeitnow.com/jobs/tech-corp/senior-python-engineer-101",
            "tags": ["Python", "FastAPI", "PostgreSQL", "python"],
            "job_types": ["Full time", "Remote"],
            "location": "Berlin",
            "created_at": 1789297793,
        },
        {
            "slug": "frontend-react-lead-102",
            "company_name": "DevStudio",
            "title": "Frontend React Lead",
            "description": "<p>Frontend engineer needed for TypeScript and React dashboard.</p>",
            "remote": False,
            "url": "https://www.arbeitnow.com/jobs/devstudio/frontend-react-lead-102",
            "tags": ["React", "TypeScript"],
            "job_types": ["Full time"],
            "location": "Munich",
            "created_at": 1789297800,
        },
    ],
    "links": {"next": "https://www.arbeitnow.com/api/job-board-api?page=2"},
    "meta": {"current_page": 1, "per_page": 100},
}


# ---------------------------------------------------------------------------
# 1. ArbeitnowClient Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_arbeitnow_fetch_jobs_success():
    """Verify successful fetch and deserialization of Arbeitnow job listings."""
    route = respx.get("https://www.arbeitnow.com/api/job-board-api").respond(
        status_code=200,
        json=SAMPLE_ARBEITNOW_PAYLOAD,
    )

    async with ArbeitnowClient() as client:
        jobs = await client.fetch_jobs(page=1)

    assert route.called
    assert len(jobs) == 2
    assert jobs[0].slug == "senior-python-engineer-101"
    assert jobs[0].company_name == "Tech Corp"
    assert jobs[0].remote is True
    assert jobs[0].created_at == 1789297793


@pytest.mark.asyncio
@respx.mock
async def test_arbeitnow_fetch_jobs_page_param():
    """Verify page query parameter is correctly passed when page > 1."""
    route = respx.get("https://www.arbeitnow.com/api/job-board-api", params={"page": "2"}).respond(
        status_code=200,
        json={"data": [], "links": {}, "meta": {}},
    )

    async with ArbeitnowClient() as client:
        jobs = await client.fetch_jobs(page=2)

    assert route.called
    assert len(jobs) == 0


@pytest.mark.asyncio
@respx.mock
async def test_arbeitnow_rate_limit_429():
    """Verify HTTP 429 raises RateLimitExceededError with extracted Retry-After."""
    respx.get("https://www.arbeitnow.com/api/job-board-api").respond(
        status_code=429,
        headers={"Retry-After": "7"},
    )

    async with ArbeitnowClient() as client:
        with pytest.raises(RateLimitExceededError) as exc_info:
            await client.fetch_jobs()

    assert exc_info.value.retry_after == 7.0
    assert exc_info.value.provider == "arbeitnow"


@pytest.mark.asyncio
@respx.mock
async def test_arbeitnow_upstream_500_retries():
    """Verify 5xx server errors trigger retries and ultimately raise UpstreamServiceError."""
    respx.get("https://www.arbeitnow.com/api/job-board-api").respond(
        status_code=503,
    )

    async with ArbeitnowClient() as client:
        with pytest.raises(UpstreamServiceError) as exc_info:
            await client.fetch_jobs()

    assert exc_info.value.status_code == 502
    assert exc_info.value.upstream_status_code == 503
    assert exc_info.value.provider == "arbeitnow"


@pytest.mark.asyncio
@respx.mock
async def test_arbeitnow_timeout_exception():
    """Verify socket timeouts are mapped to DiscoveryTimeoutError."""
    respx.get("https://www.arbeitnow.com/api/job-board-api").mock(
        side_effect=httpx.ReadTimeout("Socket timed out"),
    )

    async with ArbeitnowClient() as client:
        with pytest.raises(DiscoveryTimeoutError) as exc_info:
            await client.fetch_jobs()

    assert exc_info.value.provider == "arbeitnow"


@pytest.mark.asyncio
@respx.mock
async def test_arbeitnow_malformed_json():
    """Verify unparseable responses raise MalformedPayloadError."""
    respx.get("https://www.arbeitnow.com/api/job-board-api").respond(
        status_code=200,
        text="<!DOCTYPE html><html>Service Unavailable</html>",
        headers={"Content-Type": "text/html"},
    )

    async with ArbeitnowClient() as client:
        with pytest.raises(MalformedPayloadError) as exc_info:
            await client.fetch_jobs()

    assert exc_info.value.provider == "arbeitnow"


# ---------------------------------------------------------------------------
# 2. ArbeitnowMapper Tests
# ---------------------------------------------------------------------------


def test_arbeitnow_mapper_to_raw_lead():
    """Verify mapping of ArbeitnowJobItem to canonical RawLead."""
    job = ArbeitnowJobItem(
        slug="backend-engineer-55",
        company_name="Acme Corp, Inc.",
        title="Senior Backend Engineer",
        description="<p>We are hiring!<br>FastAPI &amp; PostgreSQL.</p>",
        remote=True,
        url="https://www.arbeitnow.com/jobs/backend-engineer-55",
        tags=["Python", "FastAPI", "python"],
        job_types=["Full time"],
        location="Munich",
        created_at=1789297793,
    )

    raw_lead = ArbeitnowMapper.to_raw_lead(job)

    assert raw_lead is not None
    assert raw_lead.source == LeadSource.ARBEITNOW
    assert raw_lead.source_id == "backend-engineer-55"
    assert raw_lead.source_url == "https://www.arbeitnow.com/jobs/backend-engineer-55"
    assert raw_lead.company_name == "Acme Corp, Inc."
    assert raw_lead.title == "Senior Backend Engineer"
    assert "We are hiring!\nFastAPI & PostgreSQL." in raw_lead.description
    assert raw_lead.is_remote is True
    assert raw_lead.location == "Munich"
    assert raw_lead.skills_raw == ["python", "fastapi"]
    assert raw_lead.posted_at == datetime.fromtimestamp(1789297793, tz=timezone.utc)
    assert raw_lead.raw_metadata["job_types"] == ["Full time"]


def test_arbeitnow_mapper_empty_description_fallback():
    """Verify empty description falls back to title."""
    job = ArbeitnowJobItem(
        slug="test-slug-1",
        company_name="Acme",
        title="Data Scientist",
        description="",
        remote=False,
        url="https://arbeitnow.com/jobs/test-1",
    )

    raw_lead = ArbeitnowMapper.to_raw_lead(job)

    assert raw_lead is not None
    assert raw_lead.description == "Data Scientist"


def test_arbeitnow_mapper_remote_location_defaulting():
    """Verify remote=True without location defaults to 'Remote'."""
    job = ArbeitnowJobItem(
        slug="test-slug-2",
        company_name="CloudCo",
        title="DevOps Lead",
        description="Kubernetes & Terraform",
        remote=True,
        location=None,
        url="https://arbeitnow.com/jobs/test-2",
    )

    raw_lead = ArbeitnowMapper.to_raw_lead(job)

    assert raw_lead is not None
    assert raw_lead.is_remote is True
    assert raw_lead.location == "Remote"


def test_arbeitnow_mapper_missing_essential_fields():
    """Verify records missing company_name or title return None."""
    job_no_company = ArbeitnowJobItem(
        slug="bad-1",
        company_name="  ",
        title="Engineer",
        url="https://arbeitnow.com/bad-1",
    )
    job_no_title = ArbeitnowJobItem(
        slug="bad-2",
        company_name="Company",
        title=" ",
        url="https://arbeitnow.com/bad-2",
    )

    assert ArbeitnowMapper.to_raw_lead(job_no_company) is None
    assert ArbeitnowMapper.to_raw_lead(job_no_title) is None


def test_arbeitnow_mapper_map_many():
    """Verify batch mapping drops invalid records and returns valid list."""
    jobs = [
        ArbeitnowJobItem(slug="j1", company_name="Co1", title="Role1", url="https://a.com/1"),
        ArbeitnowJobItem(slug="j2", company_name="  ", title="Role2", url="https://a.com/2"),
        ArbeitnowJobItem(slug="j3", company_name="Co3", title="Role3", url="https://a.com/3"),
    ]

    leads = ArbeitnowMapper.map_many(jobs)

    assert len(leads) == 2
    assert leads[0].source_id == "j1"
    assert leads[1].source_id == "j3"


# ---------------------------------------------------------------------------
# 3. Pipeline Integration Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pipeline_orchestration_with_arbeitnow():
    """Verify pipeline coordinates HN, Remotive, and Arbeitnow with telemetry."""
    repo = AsyncMock()
    repo.list_leads.return_value = []
    repo.save_bulk.side_effect = lambda leads: leads

    mock_hn = AsyncMock()
    mock_hn.fetch_hn_hiring_thread.return_value = (
        None,
        [
            HnCommentHit(
                objectID="901",
                comment_text="Acme Corp | Python Engineer | Remote | We build FastAPI apps",
                author="dev",
            )
        ],
    )

    mock_remotive = AsyncMock()
    mock_remotive.fetch_remote_jobs.return_value = [
        RemotiveJobItem(
            id=902,
            company_name="RemoteCo",
            title="FastAPI Backend Lead",
            description="Build APIs with Python and Docker",
            url="https://remotive.com/job/902",
        )
    ]

    mock_arbeitnow = AsyncMock()
    mock_arbeitnow.fetch_jobs.return_value = [
        ArbeitnowJobItem(
            slug="arbeitnow-903",
            company_name="EuroTech",
            title="Senior Python Architect",
            description="Leading FastAPI microservices and PostgreSQL",
            remote=True,
            url="https://arbeitnow.com/jobs/903",
            tags=["Python", "FastAPI"],
        )
    ]

    pipeline = DiscoveryPipelineService(
        repository=repo,
        hn_client=mock_hn,
        remotive_client=mock_remotive,
        arbeitnow_client=mock_arbeitnow,
        dedup_service=DedupService(),
        scoring_engine=SkillMatchingEngine(),
    )

    result = await pipeline.run(hn_limit=10, remotive_limit=10, arbeitnow_page=1)

    assert result.total_fetched == 3
    assert result.hn_fetched == 1
    assert result.remotive_fetched == 1
    assert result.arbeitnow_fetched == 1
    assert result.total_unique == 3
    assert result.persisted_count == 3
    assert repo.save_bulk.called


@pytest.mark.asyncio
async def test_pipeline_bulkhead_isolation_arbeitnow_failure():
    """Verify Arbeitnow failure does not abort HN and Remotive ingestion."""
    repo = AsyncMock()
    repo.list_leads.return_value = []
    repo.save_bulk.side_effect = lambda leads: leads

    mock_hn = AsyncMock()
    mock_hn.fetch_hn_hiring_thread.return_value = (
        None,
        [
            HnCommentHit(
                objectID="911",
                comment_text="SolarCorp | Python Engineer | Remote | FastAPI and Redis",
                author="founder",
            )
        ],
    )

    mock_remotive = AsyncMock()
    mock_remotive.fetch_remote_jobs.return_value = [
        RemotiveJobItem(
            id=912,
            company_name="CloudCo",
            title="Python Developer",
            description="FastAPI, PostgreSQL",
            url="https://remotive.com/912",
        )
    ]

    mock_arbeitnow = AsyncMock()
    mock_arbeitnow.fetch_jobs.side_effect = UpstreamServiceError(
        provider="arbeitnow",
        status_code=500,
    )

    pipeline = DiscoveryPipelineService(
        repository=repo,
        hn_client=mock_hn,
        remotive_client=mock_remotive,
        arbeitnow_client=mock_arbeitnow,
        dedup_service=DedupService(),
        scoring_engine=SkillMatchingEngine(),
    )

    result = await pipeline.run()

    assert result.total_fetched == 2
    assert result.hn_fetched == 1
    assert result.remotive_fetched == 1
    assert result.arbeitnow_fetched == 0
    assert "arbeitnow" in result.provider_errors
    assert result.persisted_count == 2
