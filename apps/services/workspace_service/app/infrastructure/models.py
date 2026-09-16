"""
SQLAlchemy ORM models for Workspace & Membership persistence subsystem.

Design Patterns:
- Data Mapper Pattern: Maps relational database rows to domain entities.
- Factory Method: `to_domain` and `from_domain` translate between domain and persistence layers.
- Multi-Tenancy: Explicit owner_id and indexed tenant_type for RLS isolation.
"""

from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.services.workspace_service.app.domain.models import Workspace, ExperienceLevel,JobSearchStatus, UserJobProfile,WorkspaceMember
from apps.services.workspace_service.app.domain.roles import TenantType, WorkspaceRole
from shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.ext.mutable import MutableList  
 
 
 


class WorkspaceModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQLAlchemy ORM Model representing the 'workspaces' database table.
    Enforces multi-tenant architectural scopes for Leadforix context isolation.
    """

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Multi-tenancy scopes
    tenant_type: Mapped[str] = mapped_column(
        String(30),
        default=TenantType.JOB_SEEKER.value,
        nullable=False,
        index=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    members: Mapped[list["WorkspaceMemberModel"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    def to_domain(self) -> Workspace:
        return Workspace(
            id=self.id,
            name=self.name,
            slug=self.slug,
            owner_id=self.owner_id,
            tenant_type=TenantType(self.tenant_type),
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, domain: Workspace) -> "WorkspaceModel":
        return cls(
            id=domain.id,
            name=domain.name,
            slug=domain.slug,
            owner_id=domain.owner_id,
            tenant_type=domain.tenant_type.value,
            is_active=domain.is_active,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )


class WorkspaceMemberModel(Base, UUIDPrimaryKeyMixin):
    """
    SQLAlchemy ORM Model representing the 'workspace_members' database table.
    """

    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member_workspace_user"),
        Index("ix_workspace_members_user_id", "user_id"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=WorkspaceRole.MEMBER.value,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    workspace: Mapped["WorkspaceModel"] = relationship(
        back_populates="members",
    )

    def to_domain(self) -> WorkspaceMember:
        return WorkspaceMember(
            id=self.id,
            workspace_id=self.workspace_id,
            user_id=self.user_id,
            role=WorkspaceRole(self.role),
            joined_at=self.joined_at,
        )

    @classmethod
    def from_domain(cls, domain: WorkspaceMember) -> "WorkspaceMemberModel":
        return cls(
            id=domain.id,
            workspace_id=domain.workspace_id,
            user_id=domain.user_id,
            role=domain.role.value,
            joined_at=domain.joined_at,
        )


# Model for Jobseeker user profile in workspace
class UserJobProfileModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQLAlchemy ORM Model representing the 'user_job_profiles' database table.
    Stores job targeting and skill parameters powering the lead discovery scoring engine.
    """

    __tablename__ = "user_job_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # Dynamic criteria stored efficiently in JSONB
    # FIX: Wrapped in MutableList.as_mutable and changed default to a lambda factory
    target_titles: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSONB),
        nullable=False,
        default=lambda: [],
    )
    primary_skills: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSONB),
        nullable=False,
        default=lambda: [],
    )
    target_locations: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSONB),
        nullable=False,
        default=lambda: [],
    )

    is_remote_only: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    experience_level: Mapped[str] = mapped_column(
        String(30),
        default=ExperienceLevel.MID.value,
        nullable=False,
    )
    min_salary_usd: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    search_status: Mapped[str] = mapped_column(
        String(30),
        default=JobSearchStatus.ACTIVELY_LOOKING.value,
        nullable=False,
    )

    def to_domain(self) -> UserJobProfile:
        return UserJobProfile(
            id=self.id,
            user_id=self.user_id,
            workspace_id=self.workspace_id,
            target_titles=list(self.target_titles or []),
            primary_skills=list(self.primary_skills or []),
            target_locations=list(self.target_locations or []),
            is_remote_only=self.is_remote_only,
            experience_level=ExperienceLevel(self.experience_level),
            min_salary_usd=self.min_salary_usd,
            search_status=JobSearchStatus(self.search_status),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, domain: UserJobProfile) -> "UserJobProfileModel":
        return cls(
            id=domain.id,
            user_id=domain.user_id,
            workspace_id=domain.workspace_id,
            target_titles=domain.target_titles,
            primary_skills=domain.primary_skills,
            target_locations=domain.target_locations,
            is_remote_only=domain.is_remote_only,
            experience_level=domain.experience_level.value,
            min_salary_usd=domain.min_salary_usd,
            search_status=domain.search_status.value,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )