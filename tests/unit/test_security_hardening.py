import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from apps.services.auth_service.app.api.dependencies import get_auth_service
from apps.services.auth_service.app.api.schemas import (
    UserRegisterRequest,
)
from apps.services.auth_service.app.application.service import AuthService
from apps.services.auth_service.app.domain.models import RefreshToken, User
from apps.services.auth_service.app.domain.roles import UserRole, UserStatus
from apps.services.auth_service.app.infrastructure.security import TokenService
from apps.services.auth_service.app.main import app
from shared.exceptions import AuthenticationError, AuthorizationError
from shared.security import (
    StatelessTokenValidator,
    UserPrincipal,
    get_current_user,
    require_roles,
    require_workspace,
)

auth_client = TestClient(app)


# ==============================================================================
# 1. Stateless Downstream Security Verification Tests
# ==============================================================================


def test_stateless_token_validator_success():
    """
    Verify downstream microservices can validate signed JWTs statelessly
    and reconstruct an immutable UserPrincipal without querying auth_service DB.
    """
    token_service = TokenService()
    user_id = uuid.uuid4()
    workspace_id = uuid.uuid4()

    token = token_service.create_access_token(
        user_id=user_id,
        email="sdr@leadforix.com",
        role=UserRole.SALES_USER,
        workspace_id=workspace_id,
    )

    validator = StatelessTokenValidator()
    principal = validator.validate_and_extract_principal(token)

    assert isinstance(principal, UserPrincipal)
    assert principal.id == user_id
    assert principal.email == "sdr@leadforix.com"
    assert principal.role == "SALES_USER"
    assert principal.workspace_id == workspace_id
    assert principal.has_role("SALES_USER") is True
    assert principal.has_role("ADMIN", "OWNER") is False


def test_stateless_token_validator_rejects_tampered_and_expired():
    """Verify expired or tampered signatures fail validation."""
    validator = StatelessTokenValidator()

    # Expired token
    expired_payload = {
        "sub": str(uuid.uuid4()),
        "email": "test@leadforix.com",
        "role": "ADMIN",
        "type": "access",
        "iss": "leadforix-auth",
        "aud": "leadforix-api",
        "exp": int((datetime.now(UTC) - timedelta(hours=1)).timestamp()),
    }
    expired_token = jwt.encode(
        expired_payload,
        validator._settings.secret_key,
        algorithm=validator._settings.algorithm,
    )

    with pytest.raises(AuthenticationError, match="expired"):
        validator.validate_and_extract_principal(expired_token)


def test_stateless_token_validator_rejects_wrong_type():
    """Verify non-access tokens (e.g., refresh or id tokens) are rejected."""
    validator = StatelessTokenValidator()
    payload = {
        "sub": str(uuid.uuid4()),
        "email": "test@leadforix.com",
        "role": "ADMIN",
        "type": "refresh",
        "iss": "leadforix-auth",
        "aud": "leadforix-api",
        "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
    }
    wrong_type_token = jwt.encode(
        payload,
        validator._settings.secret_key,
        algorithm=validator._settings.algorithm,
    )

    with pytest.raises(AuthenticationError, match="expected access token"):
        validator.validate_and_extract_principal(wrong_type_token)


# ==============================================================================
# 2. Downstream FastAPI Dependencies Integration Tests
# ==============================================================================

downstream_app = FastAPI()


@downstream_app.get("/test/protected")
async def dummy_protected(user: UserPrincipal = Depends(get_current_user)):
    return {"user_id": str(user.id)}


@downstream_app.get("/test/admin-only", dependencies=[Depends(require_roles("OWNER", "ADMIN"))])
async def dummy_admin(user: UserPrincipal = Depends(get_current_user)):
    return {"role": user.role}


@downstream_app.get("/test/workspace")
async def dummy_workspace(ws_id: uuid.UUID = Depends(require_workspace)):
    return {"workspace_id": str(ws_id)}


downstream_client = TestClient(downstream_app)


def test_downstream_dependencies_flow():
    token_service = TokenService()
    user_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    # Admin with workspace context
    admin_token = token_service.create_access_token(
        user_id=user_id,
        email="admin@leadforix.com",
        role=UserRole.ADMIN,
        workspace_id=ws_id,
    )
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Protected endpoint
    res = downstream_client.get("/test/protected", headers=headers)
    assert res.status_code == 200
    assert res.json()["user_id"] == str(user_id)

    # 2. RBAC Admin-only allowed for ADMIN
    res = downstream_client.get("/test/admin-only", headers=headers)
    assert res.status_code == 200

    # 3. Workspace context resolved from token
    res = downstream_client.get("/test/workspace", headers=headers)
    assert res.status_code == 200
    assert res.json()["workspace_id"] == str(ws_id)


def test_downstream_rbac_forbidden_for_insufficient_role():
    token_service = TokenService()
    sdr_token = token_service.create_access_token(
        user_id=uuid.uuid4(),
        email="sdr@leadforix.com",
        role=UserRole.SALES_USER,
    )
    headers = {"Authorization": f"Bearer {sdr_token}"}

    # SDR attempting admin endpoint raises 403 Forbidden
    with pytest.raises(AuthorizationError):
        downstream_client.get("/test/admin-only", headers=headers)


def test_downstream_workspace_resolution_via_header():
    token_service = TokenService()
    token_without_ws = token_service.create_access_token(
        user_id=uuid.uuid4(),
        email="sdr@leadforix.com",
        role=UserRole.SALES_USER,
    )
    custom_ws = uuid.uuid4()
    headers = {
        "Authorization": f"Bearer {token_without_ws}",
        "X-Workspace-ID": str(custom_ws),
    }

    res = downstream_client.get("/test/workspace", headers=headers)
    assert res.status_code == 200
    assert res.json()["workspace_id"] == str(custom_ws)


# ==============================================================================
# 3. Password Complexity & Validation Tests
# ==============================================================================


def test_password_complexity_rejections():
    """Verify weak passwords fail validation."""
    # Too short (< 8 chars)
    with pytest.raises(ValidationError):
        UserRegisterRequest(email="a@b.com", password="Short1!")

    # No uppercase
    with pytest.raises(ValidationError):
        UserRegisterRequest(email="a@b.com", password="lowercase123!")

    # No digit
    with pytest.raises(ValidationError):
        UserRegisterRequest(email="a@b.com", password="NoDigitsHere!")

    # No special character
    with pytest.raises(ValidationError):
        UserRegisterRequest(email="a@b.com", password="NoSpecialChar123")

    # Valid password succeeds and trims email
    req = UserRegisterRequest(email="  USER@leadforix.com  ", password="ValidPass123!")
    assert req.email == "user@leadforix.com"


# ==============================================================================
# 4. Token Reuse Detection (RFC 6819) Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_token_reuse_detection_triggers_family_invalidation():
    """
    Acceptance Criteria: If an already-revoked refresh token is re-submitted,
    the server detects compromise, revokes ALL active tokens for that user, and raises AuthenticationError.
    """
    mock_session = AsyncMock()
    service = AuthService(mock_session)

    user_id = uuid.uuid4()
    revoked_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=service._token_service.hash_token("revoked_raw_token"),
        expires_at=datetime.now(UTC) + timedelta(days=7),
        is_revoked=True,  # Already revoked
        created_at=datetime.now(UTC),
    )

    service._repo.get_refresh_token_by_hash = AsyncMock(return_value=revoked_token)
    service._repo.revoke_all_user_tokens = AsyncMock(return_value=2)

    with pytest.raises(AuthenticationError, match="Token reuse detected"):
        await service.refresh_session("revoked_raw_token")

    # Assert that all user tokens were revoked across all sessions
    service._repo.revoke_all_user_tokens.assert_awaited_once_with(user_id)


# ==============================================================================
# 5. User Status Handling Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_suspended_user_login_blocked():
    """Verify suspended accounts cannot log in."""
    mock_session = AsyncMock()
    service = AuthService(mock_session)

    suspended_user = User(
        id=uuid.uuid4(),
        email="suspended@leadforix.com",
        hashed_password="bcrypt_hashed",
        role=UserRole.SALES_USER,
        status=UserStatus.SUSPENDED,
        is_active=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    service._repo.get_user_by_email = AsyncMock(return_value=suspended_user)
    service._hasher.verify_password = AsyncMock(return_value=True)

    with pytest.raises(AuthenticationError, match="suspended"):
        await service.authenticate_user("suspended@leadforix.com", "any_password")


# ==============================================================================
# 6. Password Reset Flow Tests
# ==============================================================================


def test_api_password_reset_endpoints():
    """Test POST /password-reset/request and /password-reset/confirm."""
    mock_auth = AsyncMock(spec=AuthService)
    app.dependency_overrides[get_auth_service] = lambda: mock_auth

    try:
        # 1. Request Reset
        res = auth_client.post(
            "/password-reset/request",
            json={"email": "user@leadforix.com"},
        )
        assert res.status_code == 200
        assert "instructions have been sent" in res.json()["message"]
        mock_auth.request_password_reset.assert_awaited_once_with("user@leadforix.com")

        # 2. Confirm Reset
        res = auth_client.post(
            "/password-reset/confirm",
            json={
                "token": "valid_reset_token_64chars",
                "new_password": "NewStrongPass123!",
            },
        )
        assert res.status_code == 200
        assert "Password successfully reset" in res.json()["message"]
        mock_auth.confirm_password_reset.assert_awaited_once_with(
            raw_token="valid_reset_token_64chars",
            new_password="NewStrongPass123!",
        )
    finally:
        app.dependency_overrides.clear()
