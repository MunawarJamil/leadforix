"""
Unit and orchestration tests for the Lead Discovery Pipeline, Celery task, and API routes.

Design Patterns:
- Test Double / Mocking: Isolates network I/O, Redis, and database sessions.
- Fault Injection: Injects partial failures (429 rate limits, 5xx errors) to verify Bulkhead isolation.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from apps.services.lead_service.app.api.routes import router as discovery_router
from apps.services.lead_service.app.application.dedup.service import DedupService
from apps.services.lead_service.app.application.pipeline import DiscoveryPipelineService, DiscoveryResult
from apps.services.lead_service.app.application.scoring import SkillConfig, SkillMatchingEngine
from apps.services.lead_service.app.domain.exceptions import RateLimitExceededError, UpstreamServiceError
from apps.services.lead_service.app.domain.models import Lead, LeadSource, LeadStatus, RawLead
from apps.services.lead_service.app.infrastructure.clients.schemas import (
    HnCommentHit,
    HnStoryHit,
    RemotiveJobItem,
)
from apps.services.lead_service.app.infrastructure.tasks import discover_leads_task
from shared.exceptions import register_exception_handlers
from shared.security import UserPrincipal
from shared.security.dependencies import get_current_user
from shared.security.roles import UserRole


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Mock LeadRepository simulating database operations."""
    repo = AsyncMock()
    repo.list_leads.return_value = []
    repo.save_bulk.side_effect = lambda leads: leads
    return repo


@pytest.fixture
def sample_hn_comment() -> HnCommentHit:
    """Sample HN comment hit matching parser conventions."""
    return HnCommentHit(
        objectID="1001",
        comment_text="<p>Acme Corp | Senior Python Engineer | Remote | $140k-$180k<br>We build backend APIs with FastAPI, PostgreSQL, and Docker.</p>",
        created_at="2026-09-01T12:00:00Z",
        author="acme_founder",
        story_id=999,
        parent_id=999,
    )


@pytest.fixture
def sample_remotive_job() -> RemotiveJobItem:
    """Sample Remotive job item."""
    return RemotiveJobItem(
        id=2001,
        url="https://remotive.com/jobs/beta-technologies-backend-dev-2001",
        title="Python & Go Engineer",
        company_name="Beta Technologies",
        category="software-dev",
        tags=["python", "go", "fastapi", "docker"],
        job_type="full_time",
        publication_date="2026-09-01T14:00:00",
        candidate_required_location="Worldwide",
        salary="$120k-$150k",
        description="<p>Looking for a strong Python and Go engineer with Docker and Redis experience.</p>",
    )


# =====================================================================
# 1. Pipeline Service Layer Tests
# =====================================================================

@pytest.mark.asyncio
async def test_pipeline_run_success_both_providers(
    mock_repository: AsyncMock,
    sample_hn_comment: HnCommentHit,
    sample_remotive_job: RemotiveJobItem,
) -> None:
    """Verifies successful end-to-end execution when both providers respond."""
    hn_client = AsyncMock()
    story = HnStoryHit(objectID="999", title="Ask HN: Who is hiring? (September 2026)")
    hn_client.fetch_hn_hiring_thread.return_value = (story, [sample_hn_comment])

    remotive_client = AsyncMock()
    remotive_client.fetch_remote_jobs.return_value = [sample_remotive_job]

    pipeline = DiscoveryPipelineService(
        repository=mock_repository,
        hn_client=hn_client,
        remotive_client=remotive_client,
    )

    result = await pipeline.run(hn_limit=10, remotive_limit=10)

    assert isinstance(result, DiscoveryResult)
    assert result.total_fetched == 2
    assert result.hn_fetched == 1
    assert result.remotive_fetched == 1
    assert result.duplicates_dropped == 0
    assert result.total_unique == 2
    assert result.persisted_count == 2
    assert result.provider_errors == {}
    mock_repository.save_bulk.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_partial_failure_hn_fails_remotive_succeeds(
    mock_repository: AsyncMock,
    sample_remotive_job: RemotiveJobItem,
) -> None:
    """Verifies Bulkhead fault isolation: HN 429 error does not abort Remotive ingestion."""
    hn_client = AsyncMock()
    hn_client.fetch_hn_hiring_thread.side_effect = RateLimitExceededError(
        provider="hn_algolia", retry_after=10.0
    )

    remotive_client = AsyncMock()
    remotive_client.fetch_remote_jobs.return_value = [sample_remotive_job]

    pipeline = DiscoveryPipelineService(
        repository=mock_repository,
        hn_client=hn_client,
        remotive_client=remotive_client,
    )

    result = await pipeline.run(hn_limit=10, remotive_limit=10)

    assert result.total_fetched == 1
    assert result.hn_fetched == 0
    assert result.remotive_fetched == 1
    assert result.persisted_count == 1
    assert "hacker_news" in result.provider_errors
    assert "remotive" not in result.provider_errors


@pytest.mark.asyncio
async def test_pipeline_partial_failure_remotive_fails_hn_succeeds(
    mock_repository: AsyncMock,
    sample_hn_comment: HnCommentHit,
) -> None:
    """Verifies Bulkhead fault isolation: Remotive 502 error does not abort HN ingestion."""
    hn_client = AsyncMock()
    story = HnStoryHit(objectID="999", title="Ask HN: Who is hiring? (September 2026)")
    hn_client.fetch_hn_hiring_thread.return_value = (story, [sample_hn_comment])

    remotive_client = AsyncMock()
    remotive_client.fetch_remote_jobs.side_effect = UpstreamServiceError(
        provider="remotive", status_code=502
    )

    pipeline = DiscoveryPipelineService(
        repository=mock_repository,
        hn_client=hn_client,
        remotive_client=remotive_client,
    )

    result = await pipeline.run(hn_limit=10, remotive_limit=10)

    assert result.total_fetched == 1
    assert result.hn_fetched == 1
    assert result.remotive_fetched == 0
    assert result.persisted_count == 1
    assert "remotive" in result.provider_errors
    assert "hacker_news" not in result.provider_errors


@pytest.mark.asyncio
async def test_pipeline_both_providers_fail(
    mock_repository: AsyncMock,
) -> None:
    """Verifies pipeline gracefully returns 0 results when all upstream providers fail."""
    hn_client = AsyncMock()
    hn_client.fetch_hn_hiring_thread.side_effect = UpstreamServiceError(provider="hn", status_code=503)

    remotive_client = AsyncMock()
    remotive_client.fetch_remote_jobs.side_effect = UpstreamServiceError(provider="remotive", status_code=503)

    pipeline = DiscoveryPipelineService(
        repository=mock_repository,
        hn_client=hn_client,
        remotive_client=remotive_client,
    )

    result = await pipeline.run()

    assert result.total_fetched == 0
    assert result.persisted_count == 0
    assert "hacker_news" in result.provider_errors
    assert "remotive" in result.provider_errors
    mock_repository.save_bulk.assert_not_called()


@pytest.mark.asyncio
async def test_pipeline_deduplication_filters_duplicates(
    mock_repository: AsyncMock,
    sample_hn_comment: HnCommentHit,
) -> None:
    """Verifies that duplicates between history and candidate batch are dropped."""
    # Simulate an existing historical lead matching sample_hn_comment
    existing_lead = Lead(
        id=uuid4(),
        company_name="Acme Corp",
        title="Senior Python Engineer",
        description="Historical lead description",
        source=LeadSource.HACKER_NEWS,
        source_url="https://news.ycombinator.com/item?id=1001",
        source_id="1001",
        status=LeadStatus.QUALIFIED,
        match_score=85,
    )
    mock_repository.list_leads.return_value = [existing_lead]

    hn_client = AsyncMock()
    story = HnStoryHit(objectID="999", title="Ask HN: Who is hiring?")
    hn_client.fetch_hn_hiring_thread.return_value = (story, [sample_hn_comment])

    remotive_client = AsyncMock()
    remotive_client.fetch_remote_jobs.return_value = []

    pipeline = DiscoveryPipelineService(
        repository=mock_repository,
        hn_client=hn_client,
        remotive_client=remotive_client,
    )

    result = await pipeline.run()

    assert result.total_fetched == 1
    assert result.duplicates_dropped == 1
    assert result.total_unique == 0
    assert result.persisted_count == 0


# =====================================================================
# 2. Celery Background Task Tests
# =====================================================================

def test_discover_leads_task_concurrency_lock_skipped() -> None:
    """Verifies that discover_leads_task exits cleanly when Redis lock cannot be acquired."""
    mock_redis = MagicMock()
    mock_lock = MagicMock()
    mock_lock.acquire.return_value = False  # Lock already held by another worker
    mock_redis.lock.return_value = mock_lock

    with patch("apps.services.lead_service.app.infrastructure.tasks._get_redis_client", return_value=mock_redis):
        result = discover_leads_task(hn_limit=50)

    assert result["status"] == "skipped"
    assert result["reason"] == "lock_active"
    mock_lock.acquire.assert_called_once()


# =====================================================================
# 3. FastAPI API Routes Tests
# =====================================================================

@pytest.fixture
def api_client() -> TestClient:
    """TestClient wired with discovery routes and mock authentication."""
    test_app = FastAPI()
    register_exception_handlers(test_app)
    test_app.include_router(discovery_router)

    # Mock user principal with ADMIN role
    mock_admin = UserPrincipal(
        id=uuid4(),
        email="admin@leadforix.com",
        role=UserRole.ADMIN,
        workspace_id=uuid4(),
    )
    test_app.dependency_overrides[get_current_user] = lambda: mock_admin

    return TestClient(test_app)


def test_api_trigger_discovery(api_client: TestClient) -> None:
    """Verifies POST /discovery/run triggers background Celery task and returns 202."""
    mock_task_result = MagicMock()
    mock_task_result.id = "test-task-123e4567"

    with patch("apps.services.lead_service.app.infrastructure.tasks.discover_leads_task.delay", return_value=mock_task_result):
        resp = api_client.post(
            "/discovery/run",
            json={"hn_limit": 50, "remotive_limit": 50, "save_only_qualified": True},
        )

    assert resp.status_code == 202
    data = resp.json()
    assert data["task_id"] == "test-task-123e4567"
    assert data["status"] == "PENDING"


def test_api_get_discovery_status(api_client: TestClient) -> None:
    """Verifies GET /discovery/status/{task_id} inspects AsyncResult state."""
    mock_async_result = MagicMock()
    mock_async_result.status = "SUCCESS"
    mock_async_result.ready.return_value = True
    mock_async_result.successful.return_value = True
    mock_async_result.result = {
        "status": "completed",
        "total_fetched": 45,
        "persisted_count": 30,
    }

    with patch("apps.services.lead_service.app.api.routes.AsyncResult", return_value=mock_async_result):
        resp = api_client.get("/discovery/status/test-task-123e4567")

    assert resp.status_code == 200
    data = resp.json()
    assert data["task_id"] == "test-task-123e4567"
    assert data["status"] == "SUCCESS"
    assert data["ready"] is True
    assert data["successful"] is True
    assert data["result"]["persisted_count"] == 30
