"""
Raw API response schemas (Data Transfer Objects) for Algolia HN Search and Remotive.
Design Pattern: Data Transfer Object (DTO) with Pydantic v2 strict validation.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Hacker News (Algolia Search API) DTOs
# ---------------------------------------------------------------------------


class HnStoryHit(BaseModel):
    """Represents a story item from Algolia HN search (e.g. 'Who is hiring?')."""

    model_config = ConfigDict(extra="ignore")

    objectID: str
    title: str
    created_at: str | None = None
    points: int | None = 0
    num_comments: int | None = 0


class HnCommentHit(BaseModel):
    """Represents an individual comment hit under a hiring thread."""

    model_config = ConfigDict(extra="ignore")

    objectID: str
    author: str | None = None
    comment_text: str | None = None
    story_id: int | None = None
    created_at: str | None = None
    parent_id: int | None = None


class HnSearchResponse(BaseModel):
    """Paginated search response envelope from Algolia HN API."""

    model_config = ConfigDict(extra="ignore")

    hits: list[dict[str, Any]] = Field(default_factory=list)
    nbHits: int = 0
    page: int = 0
    nbPages: int = 0
    hitsPerPage: int = 0


# ---------------------------------------------------------------------------
# Remotive Job Listing API DTOs
# ---------------------------------------------------------------------------


class RemotiveJobItem(BaseModel):
    """Represents an individual remote job listing from the Remotive API."""

    model_config = ConfigDict(extra="ignore")

    id: int
    url: str
    title: str
    company_name: str
    company_logo: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    job_type: str | None = None
    publication_date: str | None = None
    candidate_required_location: str | None = None
    salary: str | None = None
    description: str = ""


class RemotiveJobsResponse(BaseModel):
    """Top-level response envelope from Remotive remote-jobs endpoint."""

    model_config = ConfigDict(extra="ignore")

    job_count: int = Field(alias="job-count", default=0)
    jobs: list[RemotiveJobItem] = Field(default_factory=list)
