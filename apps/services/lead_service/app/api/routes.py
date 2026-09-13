"""
API endpoints for dispatching and monitoring lead discovery background tasks.

Design Patterns:
- Asynchronous Request-Reply Pattern: Accepts task submission with HTTP 202 Accepted
  and provides a task ID for subsequent status polling.
- Guard / RBAC Pattern: Restricts pipeline invocation to authenticated users with sufficient roles.
- DTO Validation: Pydantic request/response schemas with explicit input constraints.
"""

import logging
from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Path, status
from pydantic import BaseModel, Field

from apps.services.lead_service.app.infrastructure.tasks import discover_leads_task
from infrastructure.messaging.celery_app import celery_app
from shared.security import UserPrincipal, get_current_user, require_roles
from shared.security.roles import UserRole

logger = logging.getLogger("lead_service.api.discovery")

router = APIRouter(prefix="/discovery", tags=["Discovery"])


class DiscoveryTriggerRequest(BaseModel):
    """Configuration payload for triggering on-demand lead discovery."""

    hn_limit: int = Field(default=100, ge=1, le=1000, description="Max HN comments to inspect")
    remotive_limit: int | None = Field(default=100, ge=1, le=500, description="Max Remotive jobs to fetch")
    remotive_category: str = Field(default="software-dev", description="Remotive job category")
    save_only_qualified: bool = Field(
        default=False,
        description="If True, only leads meeting qualification threshold are persisted",
    )


class DiscoveryTriggerResponse(BaseModel):
    """Receipt returned upon queuing an asynchronous discovery execution."""

    task_id: str = Field(..., description="Celery background task ID")
    status: str = Field(default="PENDING", description="Initial task state")
    message: str = Field(..., description="Human-readable status summary")


class DiscoveryStatusResponse(BaseModel):
    """Current state and outcome of an asynchronous discovery job."""

    task_id: str
    status: str
    ready: bool
    successful: bool
    result: dict[str, Any] | None = None


@router.post(
    "/run",
    response_model=DiscoveryTriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger On-Demand Discovery",
    dependencies=[Depends(require_roles(UserRole.OWNER, UserRole.ADMIN, UserRole.SALES_USER))],
)
async def trigger_discovery(
    payload: DiscoveryTriggerRequest | None = None,
    current_user: UserPrincipal = Depends(get_current_user),
) -> DiscoveryTriggerResponse:
    """
    Dispatches an asynchronous discovery workflow to the Celery worker cluster.
    Returns HTTP 202 with a task ID to poll for execution completion.
    """
    req = payload or DiscoveryTriggerRequest()

    task = discover_leads_task.delay(
        hn_limit=req.hn_limit,
        remotive_limit=req.remotive_limit,
        remotive_category=req.remotive_category,
        save_only_qualified=req.save_only_qualified,
    )

    logger.info(
        "Discovery task dispatched by user",
        extra={"task_id": task.id, "user_id": str(current_user.id), "email": current_user.email},
    )

    return DiscoveryTriggerResponse(
        task_id=task.id,
        status="PENDING",
        message="Discovery workflow dispatched successfully.",
    )


@router.get(
    "/status/{task_id}",
    response_model=DiscoveryStatusResponse,
    summary="Check Discovery Task Status",
    dependencies=[Depends(get_current_user)],
)
async def get_discovery_status(
    task_id: str = Path(..., description="Celery task identifier"),
) -> DiscoveryStatusResponse:
    """
    Checks the status and result of a discovery task from the Celery result backend.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    is_ready = task_result.ready()
    is_successful = task_result.successful() if is_ready else False
    result_data = task_result.result if is_ready and isinstance(task_result.result, dict) else None

    return DiscoveryStatusResponse(
        task_id=task_id,
        status=task_result.status,
        ready=is_ready,
        successful=is_successful,
        result=result_data,
    )
