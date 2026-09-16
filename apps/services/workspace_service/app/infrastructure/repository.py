"""
Workspace Repository Pattern implementation for SQLAlchemy persistence.

Design Patterns:
- Repository Pattern: Mediates between domain and data mapping layers.
"""

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.services.workspace_service.app.domain.models import Workspace, WorkspaceMember,UserJobProfile
from apps.services.workspace_service.app.infrastructure.models import (
    WorkspaceMemberModel,
    WorkspaceModel,
    UserJobProfileModel
)

 




class WorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_workspace_by_owner_id(self, owner_id: UUID) -> Workspace | None:
        """Finds primary workspace owned by a specific user."""
        stmt = select(WorkspaceModel).where(WorkspaceModel.owner_id == owner_id).limit(1)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_workspace_by_slug(self, slug: str) -> Workspace | None:
        """Finds workspace by unique slug."""
        stmt = select(WorkspaceModel).where(WorkspaceModel.slug == slug)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def create_workspace_with_owner(
        self,
        workspace: Workspace,
        member: WorkspaceMember,
    ) -> Workspace:
        """
        Atomically persists Workspace and its OWNER membership.
        """
        workspace_model = WorkspaceModel.from_domain(workspace)
        member_model = WorkspaceMemberModel.from_domain(member)
        
        self._session.add(workspace_model)
        self._session.add(member_model)
        await self._session.flush()
        return workspace_model.to_domain()




class JobProfileRepository:
    """
    Repository pattern for UserJobProfile persistence.
    """
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    async def get_by_user_id(self, user_id: UUID) -> UserJobProfile | None:
        """Finds job seeker profile by user_id."""
        stmt = select(UserJobProfileModel).where(UserJobProfileModel.user_id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None
    async def upsert_profile(self, profile: UserJobProfile) -> UserJobProfile:
        """
        Inserts or updates a user job profile.
        """
        stmt = select(UserJobProfileModel).where(UserJobProfileModel.user_id == profile.user_id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()
        if existing_model:
            existing_model.target_titles = list(profile.target_titles)
            existing_model.primary_skills = list(profile.primary_skills)
            existing_model.target_locations = list(profile.target_locations)
            existing_model.is_remote_only = profile.is_remote_only
            existing_model.experience_level = profile.experience_level.value
            existing_model.min_salary_usd = profile.min_salary_usd
            existing_model.search_status = profile.search_status.value
            existing_model.updated_at = profile.updated_at
            await self._session.flush()
            return existing_model.to_domain()
        else:
            new_model = UserJobProfileModel.from_domain(profile)
            self._session.add(new_model)
            await self._session.flush()
            return new_model.to_domain()