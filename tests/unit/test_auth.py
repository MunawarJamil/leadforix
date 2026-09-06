import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from apps.services.auth_service.app.api.dependencies import get_auth_service
from apps.services.auth_service.app.application.service import AuthService, TokenPair
from apps.services.auth_service.app.domain.models import User
from apps.services.auth_service.app.domain.roles import UserRole
from apps.services.auth_service.app.infrastructure.security import PasswordHasher, TokenService
from apps.services.auth_service.app.main import app
from shared.exceptions import AuthenticationError, ConflictError

client = TestClient(app)


# ==============================================================================
# 1. Cryptographic & Security Primitives Tests
# ==============================================================================

def test_password_hasher_one_way_and_verification():
    """
    Verify bcrypt one-way hashing and verification.
    Acceptance Criteria: Passwords are never stored or recoverable in plaintext.
    """
    raw_password = "SuperSecretPassword123!"
    hashed = PasswordHasher.hash_password(raw_password)

    # Hash must not be plaintext and must contain bcrypt signature
    assert hashed != raw_password
    assert hashed.startswith("$2b$")

    # Correct password verifies
    assert PasswordHasher.verify_password(raw_password, hashed) is True

    # Incorrect password fails
    assert PasswordHasher.verify_password("WrongPassword!", hashed) is False


def test_token_service_access_token_lifecycle():
    """
    Verify JWT Access Token assembly, claim integrity, and signature validation.
    """
    service = TokenService()
    user_id = uuid.uuid4()
    email = "test@leadforix.com"
    role = UserRole.ADMIN

    # Issue token
    token = service.create_access_token(user_id=user_id, email=email, role=role)
    assert isinstance(token, str)

    # Decode and verify payload claims
    claims = service.decode_access_token(token)
    assert claims["sub"] == str(user_id)
    assert claims["email"] == email
    assert claims["role"] == UserRole.ADMIN.value
    assert claims["type"] == "access"


def test_token_service_rejects_tampered_or_invalid_tokens():
    """
    Acceptance Criteria: Invalid/tampered tokens are rejected.
    """
    service = TokenService()
    tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.tampered_signature"

    with pytest.raises(AuthenticationError):
        service.decode_access_token(tampered_token)


def test_token_service_refresh_token_generation():
    """
    Verify refresh token generation returns high-entropy opaque token and matching SHA-256 hash.
    """
    service = TokenService()
    raw_token, token_hash, expires_at = service.generate_refresh_token()

    assert len(raw_token) > 40
    assert len(token_hash) == 64  # SHA-256 hex length
    assert service.hash_token(raw_token) == token_hash
    assert expires_at > datetime.now(timezone.utc)


# ==============================================================================
# 2. API Flow Tests (FastAPI Dependency Injection Overrides)
# ==============================================================================

@pytest.fixture
def mock_auth_service():
    """
    Design Pattern: Test Double / Dependency Override
    Mocks AuthService to test API routes and HTTP status codes in isolation.
    """
    mock = AsyncMock(spec=AuthService)
    app.dependency_overrides[get_auth_service] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


def test_api_register_success(mock_auth_service):
    """
    Test POST /register returns 201 Created and sanitized User representation.
    """
    fake_user = User(
        id=uuid.uuid4(),
        email="sdr@leadforix.com",
        hashed_password="bcrypt-hashed-string",
        role=UserRole.SALES_USER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_auth_service.register_user.return_value = fake_user

    payload = {
        "email": "sdr@leadforix.com",
        "password": "strongPassword123!",
        "role": "SALES_USER",
    }
    response = client.post("/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "sdr@leadforix.com"
    assert data["role"] == "SALES_USER"
    assert "hashed_password" not in data  # Never leaked in API


def test_api_register_duplicate_email(mock_auth_service):
    """
    Test POST /register returns 409 Conflict when user already exists.
    """
    mock_auth_service.register_user.side_effect = ConflictError("User already exists")

    payload = {
        "email": "duplicate@leadforix.com",
        "password": "strongPassword123!",
    }
    response = client.post("/register", json=payload)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_api_login_success(mock_auth_service):
    """
    Test POST /login returns 200 OK with access and refresh token pair.
    """
    fake_tokens = TokenPair(
        access_token="fake.access.jwt",
        refresh_token="fake_refresh_token_123",
        token_type="bearer",
        expires_in=900,
    )
    fake_user = User(
        id=uuid.uuid4(),
        email="user@leadforix.com",
        hashed_password="hash",
        role=UserRole.SALES_USER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_auth_service.authenticate_user.return_value = (fake_tokens, fake_user)

    response = client.post(
        "/login",
        json={"email": "user@leadforix.com", "password": "correct_password"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "fake.access.jwt"
    assert data["refresh_token"] == "fake_refresh_token_123"
    assert data["token_type"] == "bearer"


def test_api_login_invalid_credentials(mock_auth_service):
    """
    Test POST /login returns 401 Unauthorized on wrong password.
    """
    mock_auth_service.authenticate_user.side_effect = AuthenticationError("Invalid email or password")

    response = client.post(
        "/login",
        json={"email": "user@leadforix.com", "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_api_refresh_success(mock_auth_service):
    """
    Test POST /refresh returns 200 OK with rotated token pair.
    """
    rotated_tokens = TokenPair(
        access_token="new.access.jwt",
        refresh_token="new_refresh_token_456",
        token_type="bearer",
        expires_in=900,
    )
    fake_user = User(
        id=uuid.uuid4(),
        email="user@leadforix.com",
        hashed_password="hash",
        role=UserRole.SALES_USER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_auth_service.refresh_session.return_value = (rotated_tokens, fake_user)

    response = client.post("/refresh", json={"refresh_token": "valid_refresh_token"})
    assert response.status_code == 200
    assert response.json()["access_token"] == "new.access.jwt"


def test_api_logout_success(mock_auth_service):
    """
    Test POST /logout revokes token and returns success message.
    """
    mock_auth_service.logout_user.return_value = None

    response = client.post("/logout", json={"refresh_token": "token_to_revoke"})
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


def test_api_protected_me_endpoint(mock_auth_service):
    """
    Test GET /me requires valid Bearer token and returns user profile.
    """
    user_id = uuid.uuid4()
    fake_user = User(
        id=user_id,
        email="me@leadforix.com",
        hashed_password="hash",
        role=UserRole.OWNER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_auth_service.get_user_by_id.return_value = fake_user

    # Generate a real signed access token
    token = TokenService().create_access_token(
        user_id=user_id,
        email="me@leadforix.com",
        role=UserRole.OWNER,
    )

    # 1. Calling without Bearer token fails with 401
    unauthorized_res = client.get("/me")
    assert unauthorized_res.status_code == 401

    # 2. Calling with valid Bearer token succeeds
    headers = {"Authorization": f"Bearer {token}"}
    authorized_res = client.get("/me", headers=headers)
    assert authorized_res.status_code == 200
    assert authorized_res.json()["email"] == "me@leadforix.com"
    assert authorized_res.json()["role"] == "OWNER"
