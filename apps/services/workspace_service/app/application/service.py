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

from apps.services.workspace_service.app.domain.models import Workspace, WorkspaceMember, UserJobProfile
from apps.services.workspace_service.app.domain.roles import TenantType, WorkspaceRole,   ExperienceLevel,JobSearchStatus
from apps.services.workspace_service.app.infrastructure.repository import WorkspaceRepository ,JobProfileRepository
from shared.database.session import transaction
from shared.exceptions import NotFoundError



#  workspace  service  
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
 

        # 3. Persist workspace, owner, and seed initial Job Profile
        async with transaction(self._session):
            created_ws = await self._repo.create_workspace_with_owner(workspace, member)
            
            # Auto-seed initial empty Job Profile if not already exists
            profile_repo = JobProfileRepository(self._session)
            if not await profile_repo.get_by_user_id(user_id):
                initial_profile = UserJobProfile(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    workspace_id=workspace_id,
                    target_titles=[],
                    primary_skills=[],
                    target_locations=[],
                    is_remote_only=True,
                    experience_level=ExperienceLevel.MID,
                    min_salary_usd=None,
                    search_status=JobSearchStatus.ACTIVELY_LOOKING,
                    created_at=now,
                    updated_at=now,
                )
                await profile_repo.upsert_profile(initial_profile)

            return created_ws
 



#  JobProfileService  
class JobProfileService:
    """
    Application service managing Job Seeker Profiles.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = JobProfileRepository(session)
        self._ws_repo = WorkspaceRepository(session)

    async def get_profile(self, user_id: UUID) -> UserJobProfile:
        """Retrieves profile for user, auto-creating a default one if workspace exists."""
        profile = await self._repo.get_by_user_id(user_id)
        if profile:
            return profile

        # Fallback: Agar profile na ho lekin workspace ho, to default create karein
        ws = await self._ws_repo.get_workspace_by_owner_id(user_id)
        if not ws:
            raise NotFoundError(f"No workspace or job profile found for user {user_id}")

        now = datetime.now(timezone.utc)
        default_profile = UserJobProfile(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=ws.id,
            target_titles=[],
            primary_skills=[],
            target_locations=[],
            is_remote_only=True,
            experience_level=ExperienceLevel.MID,
            min_salary_usd=None,
            search_status=JobSearchStatus.ACTIVELY_LOOKING,
            created_at=now,
            updated_at=now,
        )
        async with transaction(self._session):
            return await self._repo.upsert_profile(default_profile)

    async def update_profile(
        self,
        user_id: UUID,
        target_titles: list[str] | None = None,
        primary_skills: list[str] | None = None,
        target_locations: list[str] | None = None,
        is_remote_only: bool | None = None,
        experience_level: ExperienceLevel | None = None,
        min_salary_usd: int | None = None,
        search_status: JobSearchStatus | None = None,
    ) -> UserJobProfile:
        """Updates user's job profile preferences."""
        current = await self.get_profile(user_id)

        now = datetime.now(timezone.utc)
        updated_profile = UserJobProfile(
            id=current.id,
            user_id=current.user_id,
            workspace_id=current.workspace_id,
            target_titles=list(target_titles if target_titles is not None else current.target_titles),
            primary_skills=list(primary_skills if primary_skills is not None else current.primary_skills),
            target_locations=list(target_locations if target_locations is not None else current.target_locations),
            is_remote_only=is_remote_only if is_remote_only is not None else current.is_remote_only,
            experience_level=experience_level or current.experience_level,
            min_salary_usd=min_salary_usd if min_salary_usd is not None else current.min_salary_usd,
            search_status=search_status or current.search_status,
            created_at=current.created_at,
            updated_at=now,
        )

        async with transaction(self._session):
            return await self._repo.upsert_profile(updated_profile)
