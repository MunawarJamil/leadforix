"""
Unit tests for Tenancy & Workspace Provisioning via RabbitMQ.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest

from apps.services.auth_service.app.application.service import AuthService
from apps.services.auth_service.app.domain.models import User
from apps.services.auth_service.app.domain.roles import UserRole
from apps.services.workspace_service.app.application.service import WorkspaceService
from apps.services.workspace_service.app.domain.models import Workspace, WorkspaceMember
from apps.services.workspace_service.app.domain.roles import TenantType, WorkspaceRole
from apps.services.workspace_service.app.infrastructure.consumer import process_user_registered_event


@pytest.mark.asyncio
async def test_workspace_service_provisions_new_workspace():
    """Verifies that WorkspaceService correctly creates workspace and assigns OWNER."""
    mock_session = AsyncMock()
    user_id = uuid.uuid4()
    email = "munawar.jamil@leadforix.com"

    service = WorkspaceService(mock_session)

    # Mock repository
    mock_repo = MagicMock()
    mock_repo.get_workspace_by_owner_id = AsyncMock(return_value=None)
    
    created_ws = Workspace(
        id=uuid.uuid4(),
        name="Munawar-jamil's Workspace",
        slug=f"munawar-jamil-{str(user_id)[:8]}",
        owner_id=user_id,
        tenant_type=TenantType.JOB_SEEKER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_repo.create_workspace_with_owner = AsyncMock(return_value=created_ws)
    service._repo = mock_repo

    with patch("apps.services.workspace_service.app.application.service.transaction"):
        result = await service.provision_personal_workspace(user_id=user_id, email=email)

    assert result.owner_id == user_id
    assert "munawar-jamil" in result.slug
    assert result.tenant_type == TenantType.JOB_SEEKER
    mock_repo.create_workspace_with_owner.assert_called_once()


@pytest.mark.asyncio
async def test_workspace_service_provisioning_is_idempotent():
    """Verifies that calling provision again for same user returns existing workspace."""
    mock_session = AsyncMock()
    user_id = uuid.uuid4()

    existing_ws = Workspace(
        id=uuid.uuid4(),
        name="Existing Workspace",
        slug="existing-slug",
        owner_id=user_id,
        tenant_type=TenantType.JOB_SEEKER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    service = WorkspaceService(mock_session)
    mock_repo = MagicMock()
    mock_repo.get_workspace_by_owner_id = AsyncMock(return_value=existing_ws)
    service._repo = mock_repo

    result = await service.provision_personal_workspace(user_id=user_id, email="test@leadforix.com")

    assert result == existing_ws
    # Verify no new creation call was made
    assert not hasattr(mock_repo, "create_workspace_with_owner") or not mock_repo.create_workspace_with_owner.called


@pytest.mark.asyncio
async def test_auth_service_publishes_event_on_signup():
    """Verifies that AuthService emits 'user.registered' RabbitMQ event upon user registration."""
    mock_session = AsyncMock()
    service = AuthService(mock_session)

    # Mock user creation
    created_user = User(
        id=uuid.uuid4(),
        email="newuser@example.com",
        hashed_password="hashed_password",
        role=UserRole.SALES_USER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    service._repo.get_user_by_email = AsyncMock(return_value=None)
    service._repo.create_user = AsyncMock(return_value=created_user)
    service._hasher.hash_password = AsyncMock(return_value="hashed_password")

    with patch("apps.services.auth_service.app.application.service.publish_event", new_callable=AsyncMock) as mock_publish:
        result = await service.register_user(email="newuser@example.com", password="SecurePassword123!")

        assert result.id == created_user.id
        mock_publish.assert_called_once()
        call_kwargs = mock_publish.call_args.kwargs
        assert call_kwargs["routing_key"] == "user.registered"
        assert call_kwargs["payload"]["user_id"] == str(created_user.id)
        assert call_kwargs["payload"]["email"] == "newuser@example.com"
        assert call_kwargs["payload"]["tenant_type"] == "JOB_SEEKER"


@pytest.mark.asyncio
async def test_auth_service_registration_resilient_if_broker_fails():
    """Verifies fault tolerance: User registration succeeds even if RabbitMQ publish raises an exception."""
    mock_session = AsyncMock()
    service = AuthService(mock_session)

    created_user = User(
        id=uuid.uuid4(),
        email="resilient@example.com",
        hashed_password="hashed_password",
        role=UserRole.SALES_USER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    service._repo.get_user_by_email = AsyncMock(return_value=None)
    service._repo.create_user = AsyncMock(return_value=created_user)
    service._hasher.hash_password = AsyncMock(return_value="hashed_password")

    with patch("apps.services.auth_service.app.application.service.publish_event", side_effect=ConnectionError("Broker unreachable")):
        # Must not raise exception
        result = await service.register_user(email="resilient@example.com", password="SecurePassword123!")
        assert result.id == created_user.id


@pytest.mark.asyncio
async def test_consumer_processes_user_registered_payload():
    """Verifies that the consumer dispatches the event to WorkspaceService."""
    user_id = uuid.uuid4()
    payload = {
        "event": "user.registered",
        "user_id": str(user_id),
        "email": "consumer.test@leadforix.com",
        "tenant_type": "JOB_SEEKER",
    }

    mock_ws = Workspace(
        id=uuid.uuid4(),
        name="Consumer's Workspace",
        slug="consumer-workspace",
        owner_id=user_id,
        tenant_type=TenantType.JOB_SEEKER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch("apps.services.workspace_service.app.infrastructure.consumer.get_db_session") as mock_db, \
         patch.object(WorkspaceService, "provision_personal_workspace", new_callable=AsyncMock) as mock_provision:
        
        async def fake_session_gen():
            yield AsyncMock()

        mock_db.return_value = fake_session_gen()
        mock_provision.return_value = mock_ws

        await process_user_registered_event(payload)

        mock_provision.assert_called_once_with(
            user_id=user_id,
            email="consumer.test@leadforix.com",
            tenant_type=TenantType.JOB_SEEKER,
        )
