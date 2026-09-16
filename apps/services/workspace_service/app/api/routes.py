"""
Protected REST API routes for Workspace & Job Seeker Profile.

Design Patterns:
- Dependency Injection: Injects database sessions and authenticated user principals statelessly.
- Information Hiding: Uses typed DTO schemas; no raw database models exposed to callers.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.services.workspace_service.app.api.schemas import (
    JobProfileResponse,
    UpdateJobProfileRequest,
    WorkspaceResponse,
)
from apps.services.workspace_service.app.application.service import JobProfileService, WorkspaceService
from apps.services.workspace_service.app.domain.models import UserJobProfile, Workspace
from shared.database.session import get_db_session
from shared.exceptions import NotFoundError
from shared.security import UserPrincipal, get_current_user

router = APIRouter(tags=["Workspace & Profile"])


def _to_workspace_response(ws: Workspace) -> WorkspaceResponse:
    return WorkspaceResponse(
        id=ws.id,
        name=ws.name,
        slug=ws.slug,
        owner_id=ws.owner_id,
        tenant_type=ws.tenant_type.value,
        is_active=ws.is_active,
        created_at=ws.created_at,
    )


def _to_profile_response(profile: UserJobProfile) -> JobProfileResponse:
    return JobProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        workspace_id=profile.workspace_id,
        target_titles=profile.target_titles,
        primary_skills=profile.primary_skills,
        target_locations=profile.target_locations,
        is_remote_only=profile.is_remote_only,
        experience_level=profile.experience_level.value,
        min_salary_usd=profile.min_salary_usd,
        search_status=profile.search_status.value,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get("/workspaces/me", response_model=WorkspaceResponse)
async def get_my_workspace(
    user: UserPrincipal = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> WorkspaceResponse:
    """Retrieves the authenticated user's primary personal workspace."""
    service = WorkspaceService(session)
    ws = await service._repo.get_workspace_by_owner_id(user.id)
    if not ws:
        raise NotFoundError("Workspace not found for current user")
    return _to_workspace_response(ws)


@router.get("/profile/me", response_model=JobProfileResponse)
async def get_my_profile(
    user: UserPrincipal = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobProfileResponse:
    """Retrieves the authenticated user's job seeker preference profile."""
    service = JobProfileService(session)
    profile = await service.get_profile(user.id)
    return _to_profile_response(profile)


@router.put("/profile/me", response_model=JobProfileResponse)
async def update_my_profile(
    req: UpdateJobProfileRequest,
    user: UserPrincipal = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> JobProfileResponse:
    """Updates the authenticated user's job seeker matching parameters."""
    service = JobProfileService(session)
    updated = await service.update_profile(
        user_id=user.id,
        target_titles=req.target_titles,
        primary_skills=req.primary_skills,
        target_locations=req.target_locations,
        is_remote_only=req.is_remote_only,
        experience_level=req.experience_level,
        min_salary_usd=req.min_salary_usd,
        search_status=req.search_status,
    )
    return _to_profile_response(updated)
