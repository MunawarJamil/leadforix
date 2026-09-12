"""
Resilient asynchronous client for the Algolia Hacker News Search API.
Design Patterns:
- Dependency Injection (external or internally managed httpx.AsyncClient)
- Async Context Manager (safe socket resource lifecycle)
- Retry with Exponential Backoff (Tenacity)
- Typed Domain Exception Wrapping
"""

import logging
import time
from types import TracebackType
from typing import Any, Self

import httpx
from pydantic import ValidationError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from apps.services.lead_service.app.domain.exceptions import (
    DiscoveryClientError,
    DiscoveryTimeoutError,
    MalformedPayloadError,
    RateLimitExceededError,
    UpstreamServiceError,
)
from apps.services.lead_service.app.infrastructure.clients.schemas import (
    HnCommentHit,
    HnSearchResponse,
    HnStoryHit,
)

logger = logging.getLogger("lead_service.hn_client")


class HnAlgoliaClient:
    """Production-grade async client for fetching Hacker News hiring threads and comments."""

    PROVIDER_NAME = "hn_algolia"
    DEFAULT_BASE_URL = "https://hn.algolia.com/api/v1"

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 15.0,
        connect_timeout: float = 5.0,
    ) -> None:
        """
        Initialize client.
        Design Pattern: Dependency Injection (client can be injected or managed internally).
        """
        self._base_url = base_url.rstrip("/")
        self._timeout_config = httpx.Timeout(
            timeout=timeout,
            connect=connect_timeout,
            read=timeout,
            write=timeout,
        )
        self._external_client = client is not None
        self._client = client or httpx.AsyncClient(timeout=self._timeout_config)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close underlying HTTP client if internally managed."""
        if not self._external_client and not self._client.is_closed:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=1.0, max=10.0),
        retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException, UpstreamServiceError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _send_request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute an HTTP GET request with retries, timeouts, and rate-limit handling.
        """
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        start_time = time.monotonic()

        try:
            response = await self._client.get(url, params=params)
            duration_ms = round((time.monotonic() - start_time) * 1000, 2)

            # Handle 429 Rate Limiting
            if response.status_code == 429:
                retry_after_hdr = response.headers.get("Retry-After")
                retry_after = float(retry_after_hdr) if retry_after_hdr and retry_after_hdr.isdigit() else 5.0
                logger.warning(
                    "Rate limit encountered on HN Algolia API",
                    extra={"url": url, "retry_after": retry_after, "status_code": 429},
                )
                raise RateLimitExceededError(provider=self.PROVIDER_NAME, retry_after=retry_after)

            # Handle 5xx Upstream Server Errors
            if 500 <= response.status_code < 600:
                logger.warning(
                    "Upstream server error on HN Algolia API",
                    extra={"url": url, "status_code": response.status_code, "duration_ms": duration_ms},
                )
                raise UpstreamServiceError(provider=self.PROVIDER_NAME, status_code=response.status_code)

            # Handle 4xx Client Errors
            if response.status_code >= 400:
                logger.error(
                    "Client error on HN Algolia API",
                    extra={"url": url, "status_code": response.status_code, "duration_ms": duration_ms},
                )
                raise DiscoveryClientError(
                    message=f"HN Algolia API responded with HTTP {response.status_code}",
                    status_code=response.status_code,
                    details={"url": url, "body": response.text[:200]},
                )

            logger.info(
                "HN Algolia API request successful",
                extra={"url": url, "status_code": response.status_code, "duration_ms": duration_ms},
            )
            return response.json()

        except httpx.TimeoutException as exc:
            logger.warning("Timeout connecting to HN Algolia API: %s", str(exc))
            raise DiscoveryTimeoutError(
                provider=self.PROVIDER_NAME,
                timeout_seconds=self._timeout_config.read or 15.0,
            ) from exc
        except httpx.NetworkError as exc:
            logger.warning("Network connection error to HN Algolia API: %s", str(exc))
            raise UpstreamServiceError(
                provider=self.PROVIDER_NAME,
                status_code=503,
                details={"error": str(exc)},
            ) from exc
        except (ValueError, KeyError) as exc:
            raise MalformedPayloadError(
                provider=self.PROVIDER_NAME,
                reason=f"Failed to parse JSON response: {exc}",
            ) from exc

    async def fetch_latest_hiring_story(self) -> HnStoryHit | None:
        """
        Find the most recent 'Ask HN: Who is hiring?' submission.
        """
        params = {
            "tags": "story,author__whoishiring",
            "query": "Who is hiring",
            "hitsPerPage": 5,
        }
        data = await self._send_request("search_by_date", params=params)

        try:
            envelope = HnSearchResponse.model_validate(data)
            for raw_hit in envelope.hits:
                story = HnStoryHit.model_validate(raw_hit)
                if "who is hiring" in story.title.lower():
                    return story
            return None
        except ValidationError as exc:
            raise MalformedPayloadError(
                provider=self.PROVIDER_NAME,
                reason=f"Invalid story schema: {exc}",
            ) from exc

    async def fetch_hiring_comments(self, story_id: str, limit: int = 100) -> list[HnCommentHit]:
        """
        Fetch top-level comments under the hiring story.
        """
        params = {
            "tags": f"comment,story_{story_id}",
            "hitsPerPage": min(limit, 1000),
        }
        data = await self._send_request("search_by_date", params=params)

        try:
            envelope = HnSearchResponse.model_validate(data)
            comments: list[HnCommentHit] = []
            for raw_hit in envelope.hits:
                comment = HnCommentHit.model_validate(raw_hit)
                if comment.comment_text:
                    comments.append(comment)
            return comments
        except ValidationError as exc:
            raise MalformedPayloadError(
                provider=self.PROVIDER_NAME,
                reason=f"Invalid comment schema: {exc}",
            ) from exc

    async def fetch_hn_hiring_thread(self, limit: int = 100) -> tuple[HnStoryHit | None, list[HnCommentHit]]:
        """
        High-level orchestrator: finds latest hiring story and retrieves its comments.
        """
        story = await self.fetch_latest_hiring_story()
        if not story:
            logger.info("No active 'Who is hiring?' story found.")
            return None, []

        comments = await self.fetch_hiring_comments(story_id=story.objectID, limit=limit)
        return story, comments
