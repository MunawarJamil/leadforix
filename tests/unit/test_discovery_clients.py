"""
Unit tests for HN Algolia and Remotive resilient API clients.
Tests transient retry logic, rate limit handling, timeout mapping, and payload validation.
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx

from apps.services.lead_service.app.domain.exceptions import (
    DiscoveryClientError,
    DiscoveryTimeoutError,
    MalformedPayloadError,
    RateLimitExceededError,
    UpstreamServiceError,
)
from apps.services.lead_service.app.infrastructure.clients.hn_client import HnAlgoliaClient
from apps.services.lead_service.app.infrastructure.clients.remotive_client import RemotiveClient

# ---------------------------------------------------------------------------
# Hacker News (Algolia Search) Client Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_hn_fetch_latest_hiring_story_success():
    """Verify fetching and parsing of the latest hiring story."""
    mock_route = respx.get("https://hn.algolia.com/api/v1/search_by_date").respond(
        status_code=200,
        json={
            "hits": [
                {
                    "objectID": "41234567",
                    "title": "Ask HN: Who is hiring? (March 2026)",
                    "created_at": "2026-03-01T15:00:00.000Z",
                    "points": 350,
                    "num_comments": 420,
                },
                {
                    "objectID": "41234568",
                    "title": "Show HN: My Cool Project",
                    "created_at": "2026-03-01T14:00:00.000Z",
                },
            ],
            "nbHits": 2,
        },
    )

    async with HnAlgoliaClient() as client:
        story = await client.fetch_latest_hiring_story()

    assert mock_route.called
    assert story is not None
    assert story.objectID == "41234567"
    assert "Who is hiring" in story.title
    assert story.points == 350


@pytest.mark.asyncio
@respx.mock
async def test_hn_fetch_latest_hiring_story_none_found():
    """Verify None is returned when no matching 'Who is hiring?' story exists."""
    respx.get("https://hn.algolia.com/api/v1/search_by_date").respond(
        status_code=200,
        json={"hits": [{"objectID": "999", "title": "Unrelated Story"}], "nbHits": 1},
    )

    async with HnAlgoliaClient() as client:
        story = await client.fetch_latest_hiring_story()

    assert story is None


@pytest.mark.asyncio
@respx.mock
async def test_hn_fetch_hiring_comments_success():
    """Verify fetching comments for a given story ID."""
    respx.get("https://hn.algolia.com/api/v1/search_by_date").respond(
        status_code=200,
        json={
            "hits": [
                {
                    "objectID": "5551",
                    "author": "techfounder",
                    "comment_text": "Acme Corp | Senior Python Dev | Remote | $140k",
                    "story_id": 41234567,
                },
                {
                    "objectID": "5552",
                    "author": "devops_lead",
                    "comment_text": "CloudScale | SRE | New York | Full-time",
                    "story_id": 41234567,
                },
            ],
            "nbHits": 2,
        },
    )

    async with HnAlgoliaClient() as client:
        comments = await client.fetch_hiring_comments(story_id="41234567")

    assert len(comments) == 2
    assert comments[0].objectID == "5551"
    assert "Acme Corp" in (comments[0].comment_text or "")


@pytest.mark.asyncio
@respx.mock
async def test_hn_fetch_thread_orchestration():
    """Verify high-level fetch_hn_hiring_thread orchestrates story and comments."""
    respx.get("https://hn.algolia.com/api/v1/search_by_date").mock(
        side_effect=[
            httpx.Response(
                200,
                json={"hits": [{"objectID": "101", "title": "Ask HN: Who is hiring? (March 2026)"}]},
            ),
            httpx.Response(
                200,
                json={"hits": [{"objectID": "201", "comment_text": "Hiring Engineers"}]},
            ),
        ]
    )

    async with HnAlgoliaClient() as client:
        story, comments = await client.fetch_hn_hiring_thread()

    assert story is not None
    assert story.objectID == "101"
    assert len(comments) == 1


@pytest.mark.asyncio
@respx.mock
async def test_hn_rate_limit_handling():
    """Verify HTTP 429 raises RateLimitExceededError and extracts Retry-After."""
    respx.get("https://hn.algolia.com/api/v1/search_by_date").respond(
        status_code=429,
        headers={"Retry-After": "12"},
    )

    async with HnAlgoliaClient() as client:
        with pytest.raises(RateLimitExceededError) as exc_info:
            await client.fetch_latest_hiring_story()

    assert exc_info.value.retry_after == 12.0
    assert exc_info.value.provider == "hn_algolia"


@pytest.mark.asyncio
@respx.mock
async def test_hn_transient_error_retry_and_upstream_error():
    """Verify 500 error retries 3 times and raises UpstreamServiceError."""
    route = respx.get("https://hn.algolia.com/api/v1/search_by_date").respond(status_code=503)

    # Patch sleep to make tenacity retries instantaneous in test
    with patch("asyncio.sleep", new_callable=AsyncMock):
        async with HnAlgoliaClient() as client:
            with pytest.raises(UpstreamServiceError) as exc_info:
                await client.fetch_latest_hiring_story()

    assert route.call_count == 3  # Confirms 3 tenacity attempts
    assert exc_info.value.status_code == 502


@pytest.mark.asyncio
@respx.mock
async def test_hn_timeout_handling():
    """Verify network timeout raises DiscoveryTimeoutError."""
    respx.get("https://hn.algolia.com/api/v1/search_by_date").mock(
        side_effect=httpx.ReadTimeout("Read timed out")
    )

    with patch("asyncio.sleep", new_callable=AsyncMock):
        async with HnAlgoliaClient() as client:
            with pytest.raises(DiscoveryTimeoutError) as exc_info:
                await client.fetch_latest_hiring_story()

    assert exc_info.value.provider == "hn_algolia"


@pytest.mark.asyncio
@respx.mock
async def test_hn_malformed_payload_handling():
    """Verify corrupt response structure raises MalformedPayloadError."""
    respx.get("https://hn.algolia.com/api/v1/search_by_date").respond(
        status_code=200,
        text="this is not json {",
    )

    async with HnAlgoliaClient() as client:
        with pytest.raises(MalformedPayloadError):
            await client.fetch_latest_hiring_story()


# ---------------------------------------------------------------------------
# Remotive Client Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_remotive_fetch_jobs_success():
    """Verify fetching and parsing remote jobs from Remotive."""
    respx.get("https://remotive.com/api/remote-jobs").respond(
        status_code=200,
        json={
            "job-count": 2,
            "jobs": [
                {
                    "id": 901,
                    "url": "https://remotive.com/remote-jobs/901",
                    "title": "Staff Python Architect",
                    "company_name": "ScaleAI",
                    "category": "Software Development",
                    "tags": ["python", "fastapi", "postgres"],
                    "job_type": "full_time",
                    "candidate_required_location": "Worldwide",
                    "salary": "$150,000",
                    "description": "<p>Build high scale systems</p>",
                },
                {
                    "id": 902,
                    "url": "https://remotive.com/remote-jobs/902",
                    "title": "Senior AI Backend Engineer",
                    "company_name": "DeepTech",
                    "tags": ["python", "langchain"],
                    "description": "Looking for LLM developers",
                },
            ],
        },
    )

    async with RemotiveClient() as client:
        jobs = await client.fetch_remote_jobs(category="software-dev", limit=10)

    assert len(jobs) == 2
    assert jobs[0].id == 901
    assert jobs[0].company_name == "ScaleAI"
    assert "fastapi" in jobs[0].tags
    assert jobs[1].title == "Senior AI Backend Engineer"


@pytest.mark.asyncio
@respx.mock
async def test_remotive_rate_limit_handling():
    """Verify HTTP 429 raises RateLimitExceededError on Remotive."""
    respx.get("https://remotive.com/api/remote-jobs").respond(
        status_code=429,
        headers={"Retry-After": "30"},
    )

    async with RemotiveClient() as client:
        with pytest.raises(RateLimitExceededError) as exc_info:
            await client.fetch_remote_jobs()

    assert exc_info.value.retry_after == 30.0
    assert exc_info.value.provider == "remotive"


@pytest.mark.asyncio
@respx.mock
async def test_remotive_retry_on_server_error():
    """Verify Remotive retries on 500 error and raises UpstreamServiceError."""
    route = respx.get("https://remotive.com/api/remote-jobs").respond(status_code=500)

    with patch("asyncio.sleep", new_callable=AsyncMock):
        async with RemotiveClient() as client:
            with pytest.raises(UpstreamServiceError):
                await client.fetch_remote_jobs()

    assert route.call_count == 3


@pytest.mark.asyncio
@respx.mock
async def test_remotive_client_error_400():
    """Verify HTTP 400 client error raises DiscoveryClientError."""
    respx.get("https://remotive.com/api/remote-jobs").respond(
        status_code=400,
        text="Bad request parameters",
    )

    async with RemotiveClient() as client:
        with pytest.raises(DiscoveryClientError) as exc_info:
            await client.fetch_remote_jobs()

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
@respx.mock
async def test_remotive_malformed_json():
    """Verify invalid schema or malformed JSON raises MalformedPayloadError."""
    respx.get("https://remotive.com/api/remote-jobs").respond(
        status_code=200,
        text="<xml>Not JSON</xml>",
    )

    async with RemotiveClient() as client:
        with pytest.raises(MalformedPayloadError):
            await client.fetch_remote_jobs()
