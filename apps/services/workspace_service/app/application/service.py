"""
Application Service for Workspace Provisioning and Domain Orchestration.

Design Patterns:
- Application Service / Facade: Coordinates transactions, domain rules, and repository.
- Idempotency Pattern: Repeated provisioning requests for same user return existing workspace.
"""

from datetime import datetime, timezone
import re
import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.services.workspace_service.app.domain.models import Workspace, WorkspaceMember
from apps.services.workspace_service.app.domain.roles import TenantType, WorkspaceRole
from apps.services.workspace_service.app.infrastructure.repository import WorkspaceRepository
from shared.database.session import transaction


class WorkspaceService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = WorkspaceRepository(session)

    async def provision_personal_workspace(
        self,
        user_id: UUID,
        email: str,
        tenant_type: TenantType = TenantType.JOB_SEEKER,
    ) -> Workspace:
        """
        Idempotently provisions a personal default workspace for a registered user.
        """
        # 1. Idempotency Check: Agar user ka workspace pehle se mojood hai to wahi return karo
        existing = await self._repo.get_workspace_by_owner_id(user_id)
        if existing:
            return existing

        # 2. Derive friendly Name and unique Slug from email
        prefix = email.split("@")[0]
        clean_prefix = re.sub(r"[^a-zA-Z0-9]", "-", prefix).strip("-").lower()
        if not clean_prefix:
            clean_prefix = "workspace"

        name = f"{clean_prefix.capitalize()}'s Workspace"
        base_slug = f"{clean_prefix}-{str(user_id)[:8]}"

        now = datetime.now(timezone.utc)
        workspace_id = uuid.uuid4()

        workspace = Workspace(
            id=workspace_id,
            name=name,
            slug=base_slug,
            owner_id=user_id,
            tenant_type=tenant_type,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        member = WorkspaceMember(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            user_id=user_id,
            role=WorkspaceRole.OWNER,
            joined_at=now,
        )

        # 3. Persist atomically in transaction
        async with transaction(self._session):
            return await self._repo.create_workspace_with_owner(workspace, member)
