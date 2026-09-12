"""
Domain exceptions for discovery pipeline and API clients.
Design Pattern: Domain Exception Hierarchy (inherits from core LeadforixError).
"""

from typing import Any

from shared.exceptions.base import LeadforixError


class DiscoveryClientError(LeadforixError):
    """Base exception for all discovery upstream client failures."""

    def __init__(
        self,
        message: str = "An error occurred in discovery client",
        code: str = "DISCOVERY_CLIENT_ERROR",
        status_code: int = 502,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class RateLimitExceededError(DiscoveryClientError):
    """Raised when an upstream provider responds with HTTP 429."""

    def __init__(
        self,
        provider: str,
        retry_after: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        if retry_after is not None:
            error_details["retry_after"] = retry_after
        error_details["provider"] = provider

        super().__init__(
            message=f"Rate limit exceeded for provider '{provider}'. Retry after {retry_after}s.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=error_details,
        )
        self.retry_after = retry_after
        self.provider = provider


class UpstreamServiceError(DiscoveryClientError):
    """Raised when an upstream provider returns 5xx server errors."""

    def __init__(
        self,
        provider: str,
        status_code: int = 502,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        error_details["provider"] = provider
        super().__init__(
            message=f"Upstream provider '{provider}' failed with HTTP {status_code}",
            code="UPSTREAM_SERVICE_ERROR",
            status_code=502,
            details=error_details,
        )
        self.provider = provider
        self.upstream_status_code = status_code


class DiscoveryTimeoutError(DiscoveryClientError):
    """Raised when connection or read timeout expires after retries."""

    def __init__(
        self,
        provider: str,
        timeout_seconds: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        error_details["provider"] = provider
        error_details["timeout_seconds"] = timeout_seconds
        super().__init__(
            message=f"Request to provider '{provider}' timed out after {timeout_seconds}s",
            code="DISCOVERY_TIMEOUT",
            status_code=504,
            details=error_details,
        )
        self.provider = provider
        self.timeout_seconds = timeout_seconds



class MalformedPayloadError(DiscoveryClientError):
    """Raised when upstream returns invalid JSON or schema validation fails."""
    def __init__(
        self,
        provider: str,
        reason: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        error_details["provider"] = provider
        error_details["validation_reason"] = reason
        super().__init__(
            message=f"Received malformed payload from '{provider}': {reason}",
            code="MALFORMED_UPSTREAM_PAYLOAD",
            status_code=502,
            details=error_details,
        )
        self.provider = provider
        self.reason = reason



