"""
Workspace Repository Pattern implementation for SQLAlchemy persistence.

Design Patterns:
- Repository Pattern: Mediates between domain and data mapping layers.
"""

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.services.workspace_service.app.domain.models import Workspace, WorkspaceMember
from apps.services.workspace_service.app.infrastructure.models import (
    WorkspaceMemberModel,
    WorkspaceModel,
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
