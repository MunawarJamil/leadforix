"""
Pydantic Request/Response DTO schemas for Workspace & Job Profile APIs.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from apps.services.workspace_service.app.domain.roles import ExperienceLevel, JobSearchStatus


class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    owner_id: UUID
    tenant_type: str
    is_active: bool
    created_at: datetime


class JobProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    workspace_id: UUID
    target_titles: list[str]
    primary_skills: list[str]
    target_locations: list[str]
    is_remote_only: bool
    experience_level: str
    min_salary_usd: int | None
    search_status: str
    created_at: datetime
    updated_at: datetime


class UpdateJobProfileRequest(BaseModel):
    target_titles: list[str] | None = Field(default=None, description="Target job titles (e.g. ['Senior Backend Engineer'])")
    primary_skills: list[str] | None = Field(default=None, description="Primary technical skills (e.g. ['Python', 'FastAPI'])")
    target_locations: list[str] | None = Field(default=None, description="Preferred locations (e.g. ['Remote', 'US'])")
    is_remote_only: bool | None = Field(default=None, description="Whether to exclusively search remote roles")
    experience_level: ExperienceLevel | None = Field(default=None, description="Seniority level (ENTRY, MID, SENIOR, LEAD)")
    min_salary_usd: int | None = Field(default=None, ge=0, description="Minimum desired annual salary in USD")
    search_status: JobSearchStatus | None = Field(default=None, description="Activity status (ACTIVELY_LOOKING, OPEN_TO_OFFERS)")
