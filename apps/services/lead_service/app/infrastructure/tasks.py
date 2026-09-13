"""
Celery task implementations for asynchronous lead discovery and ingestion.

Design Patterns:
- Distributed Mutex / Lock Pattern: Enforces task idempotency and prevents concurrent runs.
- Async-to-Sync Bridge: Safely bridges Celery synchronous worker threads to async database sessions.
- Data Transfer Object / Serializer: Formats domain results into JSON-serializable task receipts.
"""

import asyncio
from datetime import datetime, timezone
import logging
import os
import redis
from typing import Any

from celery import shared_task
from apps.services.lead_service.app.application.pipeline import DiscoveryPipelineService, DiscoveryResult
from apps.services.lead_service.app.infrastructure.repository import LeadRepository
from infrastructure.messaging.celery_app import celery_app
from shared.database.session import async_session_factory

logger = logging.getLogger("lead_service.tasks")

# Redis configuration for distributed task locking
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DISCOVERY_LOCK_KEY = "lock:leadforix:lead_discovery"
DISCOVERY_LOCK_TIMEOUT_SECONDS = 600  # 10 minute lock safety ceiling


def _get_redis_client() -> redis.Redis:
    """Factory for Redis client instance."""
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


def _serialize_result(result: DiscoveryResult) -> dict[str, Any]:
    """Serializes DiscoveryResult to a JSON-safe dictionary for Celery result backend."""
    return {
        "status": "completed",
        "total_fetched": result.total_fetched,
        "hn_fetched": result.hn_fetched,
        "remotive_fetched": result.remotive_fetched,
        "duplicates_dropped": result.duplicates_dropped,
        "total_unique": result.total_unique,
        "qualified_count": result.qualified_count,
        "disqualified_count": result.disqualified_count,
        "persisted_count": result.persisted_count,
        "duration_seconds": result.duration_seconds,
        "started_at": result.started_at.isoformat(),
        "completed_at": result.completed_at.isoformat(),
        "provider_errors": result.provider_errors,
    }


async def _run_pipeline_async(
    hn_limit: int,
    remotive_limit: int | None,
    remotive_category: str,
    save_only_qualified: bool,
) -> DiscoveryResult:
    """Executes the pipeline within an isolated async DB transaction scope."""
    async with async_session_factory() as session:
        async with session.begin():
            repository = LeadRepository(session)
            pipeline = DiscoveryPipelineService(repository=repository)
            return await pipeline.run(
                hn_limit=hn_limit,
                remotive_limit=remotive_limit,
                remotive_category=remotive_category,
                save_only_qualified=save_only_qualified,
            )


@celery_app.task(
    name="lead_service.discover_leads",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def discover_leads_task(
    self,
    hn_limit: int = 100,
    remotive_limit: int | None = 100,
    remotive_category: str = "software-dev",
    save_only_qualified: bool = False,
) -> dict[str, Any]:
    """
    Celery background task orchestrating multi-source lead discovery.
    Pattern: Distributed Mutex guarded task.
    """
    redis_client = _get_redis_client()
    lock = redis_client.lock(
        name=DISCOVERY_LOCK_KEY,
        timeout=DISCOVERY_LOCK_TIMEOUT_SECONDS,
        blocking=False,
    )

    acquired = False
    try:
        acquired = lock.acquire(blocking=False)
    except Exception as exc:
        # If Redis locking encounters a connection issue, log warning and proceed carefully
        logger.warning("Unable to contact Redis for task locking: %s. Proceeding without lock.", exc)
        acquired = True

    if not acquired:
        logger.info(
            "Discovery task skipped: Another discovery process is actively executing.",
            extra={"task_id": self.request.id},
        )
        return {
            "status": "skipped",
            "reason": "lock_active",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    logger.info(
        "Beginning lead discovery background task",
        extra={"task_id": self.request.id, "hn_limit": hn_limit, "remotive_limit": remotive_limit},
    )

    try:
        # Bridge synchronous Celery worker thread to async event loop
        result = asyncio.run(
            _run_pipeline_async(
                hn_limit=hn_limit,
                remotive_limit=remotive_limit,
                remotive_category=remotive_category,
                save_only_qualified=save_only_qualified,
            )
        )
        return _serialize_result(result)

    except Exception as exc:
        logger.error(
            "Discovery task failed with unhandled exception: %s",
            str(exc),
            exc_info=True,
            extra={"task_id": self.request.id},
        )
        # Retry with exponential backoff on infrastructure failures
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries)) from exc

    finally:
        try:
            if acquired and lock.owned():
                lock.release()
        except Exception as exc:
            logger.debug("Failed releasing redis lock: %s", exc)
