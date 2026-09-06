import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
import jwt

from apps.services.auth_service.app.domain.roles import UserRole
from apps.services.auth_service.app.infrastructure.config import get_auth_settings
from shared.exceptions import AuthenticationError


class PasswordHasher:
    """
    Cryptographic Password Hashing & Verification.

    Design Patterns & Principles:
    - Single Responsibility Principle (SRP): Dedicated exclusively to credential hashing.
    - Adaptive Salting: Uses bcrypt with per-password random salts to defeat rainbow tables.
    - Timing Attack Resistance: Uses bcrypt's constant-time comparison to prevent timing side-channel attacks.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Generates a secure salted bcrypt hash for a plaintext password."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a plaintext password against a stored bcrypt hash in constant time."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False


class TokenService:
    """
    Cryptographic Token Lifecycle Service (JWT Access Tokens & Opaque Refresh Tokens).

    Design Patterns & Principles:
    - Token Pair Pattern:
        1. Short-lived Access Token (JWT): Stateless, carries user identity and roles; expires quickly (e.g. 15m).
        2. Long-lived Refresh Token (Opaque): High-entropy CSPRNG string; persisted as SHA-256 in DB.
    - Defense-in-Depth: Storing only the SHA-256 hash of refresh tokens in the database prevents
      session hijacking even if the database is exposed.
    """

    def __init__(self) -> None:
        self._settings = get_auth_settings()

    def create_access_token(
        self,
        user_id: UUID,
        email: str,
        role: UserRole,
    ) -> str:
        """
        Factory Method: Assembles and signs a short-lived RFC 7519 JSON Web Token.
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self._settings.access_token_expire_minutes)

        payload: dict[str, Any] = {
            "sub": str(user_id),
            "email": email,
            "role": role.value,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }

        return jwt.encode(
            payload,
            self._settings.secret_key,
            algorithm=self._settings.algorithm,
        )

    def decode_access_token(self, token: str) -> dict[str, Any]:
        """
        Decodes and cryptographically validates a JWT access token.
        Raises AuthenticationError on expired signatures, invalid algorithms, or malformed tokens.
        """
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm],
            )
            if payload.get("type") != "access":
                raise AuthenticationError("Invalid token type")
            return payload
        except jwt.ExpiredSignatureError as e:
            raise AuthenticationError("Access token has expired") from e
        except jwt.InvalidTokenError as e:
            raise AuthenticationError("Invalid access token") from e

    def generate_refresh_token(self) -> tuple[str, str, datetime]:
        """
        Factory Method: Generates a cryptographically strong refresh token.
        Returns:
            - raw_token: sent to the client (never saved directly in DB)
            - token_hash: SHA-256 hash stored in the DB
            - expires_at: UTC timestamp when the refresh token expires
        """
        raw_token = secrets.token_urlsafe(64)
        token_hash = self.hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self._settings.refresh_token_expire_days
        )
        return raw_token, token_hash, expires_at

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """Computes a deterministic SHA-256 digest of an opaque token for DB lookup."""
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
