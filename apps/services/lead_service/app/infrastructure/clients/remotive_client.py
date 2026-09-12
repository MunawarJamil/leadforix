"""
Resilient asynchronous client for the Remotive Remote Jobs API.
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
    RemotiveJobItem,
    RemotiveJobsResponse,
)

logger = logging.getLogger("lead_service.remotive_client")


class RemotiveClient:
    """Production-grade async client for fetching remote job opportunities from Remotive."""

    PROVIDER_NAME = "remotive"
    DEFAULT_BASE_URL = "https://remotive.com/api"

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
                    "Rate limit encountered on Remotive API",
                    extra={"url": url, "retry_after": retry_after, "status_code": 429},
                )
                raise RateLimitExceededError(provider=self.PROVIDER_NAME, retry_after=retry_after)

            # Handle 5xx Upstream Server Errors
            if 500 <= response.status_code < 600:
                logger.warning(
                    "Upstream server error on Remotive API",
                    extra={"url": url, "status_code": response.status_code, "duration_ms": duration_ms},
                )
                raise UpstreamServiceError(provider=self.PROVIDER_NAME, status_code=response.status_code)

            # Handle 4xx Client Errors
            if response.status_code >= 400:
                logger.error(
                    "Client error on Remotive API",
                    extra={"url": url, "status_code": response.status_code, "duration_ms": duration_ms},
                )
                raise DiscoveryClientError(
                    message=f"Remotive API responded with HTTP {response.status_code}",
                    status_code=response.status_code,
                    details={"url": url, "body": response.text[:200]},
                )

            logger.info(
                "Remotive API request successful",
                extra={"url": url, "status_code": response.status_code, "duration_ms": duration_ms},
            )
            return response.json()

        except httpx.TimeoutException as exc:
            logger.warning("Timeout connecting to Remotive API: %s", str(exc))
            raise DiscoveryTimeoutError(
                provider=self.PROVIDER_NAME,
                timeout_seconds=self._timeout_config.read or 15.0,
            ) from exc
        except httpx.NetworkError as exc:
            logger.warning("Network connection error to Remotive API: %s", str(exc))
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

    async def fetch_remote_jobs(
        self,
        category: str = "software-dev",
        limit: int | None = None,
    ) -> list[RemotiveJobItem]:
        """
        Fetch software development jobs from Remotive API.
        """
        params: dict[str, Any] = {"category": category}
        if limit is not None:
            params["limit"] = limit

        data = await self._send_request("remote-jobs", params=params)

        try:
            envelope = RemotiveJobsResponse.model_validate(data)
            return envelope.jobs
        except ValidationError as exc:
            raise MalformedPayloadError(
                provider=self.PROVIDER_NAME,
                reason=f"Invalid Remotive jobs schema: {exc}",
            ) from exc
