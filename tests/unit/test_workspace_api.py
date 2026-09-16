"""
Unit tests for Workspace and Job Seeker Profile REST API endpoints.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import uuid
import pytest
from fastapi.testclient import TestClient

from apps.services.workspace_service.app.domain.models import UserJobProfile, Workspace
from apps.services.workspace_service.app.domain.roles import (
    ExperienceLevel,
    JobSearchStatus,
    TenantType,
)
from apps.services.workspace_service.app.main import app
from shared.database.session import get_db_session
from shared.security import UserPrincipal, get_current_user
from shared.security.roles import UserRole

# Test principal
TEST_USER_ID = uuid.uuid4()
TEST_WORKSPACE_ID = uuid.uuid4()
TEST_PRINCIPAL = UserPrincipal(
    id=TEST_USER_ID,
    email="test.seeker@leadforix.com",
    role=UserRole.SALES_USER,
    workspace_id=TEST_WORKSPACE_ID,
)


@pytest.fixture
def client():
    """FastAPI TestClient with overridden security dependency."""
    app.dependency_overrides[get_current_user] = lambda: TEST_PRINCIPAL
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_my_workspace_success(client):
    """Verifies GET /workspaces/me returns the authenticated user's workspace."""
    mock_ws = Workspace(
        id=TEST_WORKSPACE_ID,
        name="Seeker's Workspace",
        slug="seeker-workspace",
        owner_id=TEST_USER_ID,
        tenant_type=TenantType.JOB_SEEKER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch("apps.services.workspace_service.app.infrastructure.repository.WorkspaceRepository.get_workspace_by_owner_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_ws
        response = client.get("/workspaces/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(TEST_WORKSPACE_ID)
        assert data["name"] == "Seeker's Workspace"
        assert data["slug"] == "seeker-workspace"
        assert data["tenant_type"] == "JOB_SEEKER"


def test_get_my_workspace_not_found(client):
    """Verifies GET /workspaces/me returns 404 if no workspace exists for user."""
    with patch("apps.services.workspace_service.app.infrastructure.repository.WorkspaceRepository.get_workspace_by_owner_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = client.get("/workspaces/me")

        assert response.status_code == 404
        assert response.json()["error_code"] == "NOT_FOUND"


def test_get_my_profile_success(client):
    """Verifies GET /profile/me returns the job seeker preferences."""
    mock_profile = UserJobProfile(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        workspace_id=TEST_WORKSPACE_ID,
        target_titles=["Backend Engineer", "Python Developer"],
        primary_skills=["FastAPI", "PostgreSQL", "RabbitMQ"],
        target_locations=["Remote", "US"],
        is_remote_only=True,
        experience_level=ExperienceLevel.SENIOR,
        min_salary_usd=120000,
        search_status=JobSearchStatus.ACTIVELY_LOOKING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch("apps.services.workspace_service.app.application.service.JobProfileService.get_profile", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_profile
        response = client.get("/profile/me")

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(TEST_USER_ID)
        assert "Backend Engineer" in data["target_titles"]
        assert "FastAPI" in data["primary_skills"]
        assert data["experience_level"] == "SENIOR"
        assert data["min_salary_usd"] == 120000


def test_update_my_profile_success(client):
    """Verifies PUT /profile/me updates and returns the updated job seeker preferences."""
    updated_profile = UserJobProfile(
        id=uuid.uuid4(),
        user_id=TEST_USER_ID,
        workspace_id=TEST_WORKSPACE_ID,
        target_titles=["Lead AI Engineer"],
        primary_skills=["Python", "LangGraph", "Docker"],
        target_locations=["Remote"],
        is_remote_only=True,
        experience_level=ExperienceLevel.LEAD,
        min_salary_usd=150000,
        search_status=JobSearchStatus.ACTIVELY_LOOKING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch("apps.services.workspace_service.app.application.service.JobProfileService.update_profile", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = updated_profile
        payload = {
            "target_titles": ["Lead AI Engineer"],
            "primary_skills": ["Python", "LangGraph", "Docker"],
            "target_locations": ["Remote"],
            "is_remote_only": True,
            "experience_level": "LEAD",
            "min_salary_usd": 150000,
            "search_status": "ACTIVELY_LOOKING",
        }
        response = client.put("/profile/me", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["target_titles"] == ["Lead AI Engineer"]
        assert data["experience_level"] == "LEAD"
        assert data["min_salary_usd"] == 150000


def test_workspace_service_health_probes(client):
    """Verifies liveness and readiness probes on workspace_service."""
    live_resp = client.get("/health/live")
    assert live_resp.status_code == 200
    assert live_resp.json() == {"status": "alive"}

    with patch("apps.services.workspace_service.app.main.ping_database", return_value=True):
        ready_resp = client.get("/health/ready")
        assert ready_resp.status_code == 200
        assert ready_resp.json()["status"] == "ready"
