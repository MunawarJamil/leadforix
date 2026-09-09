from typing import Any
from uuid import UUID

import jwt

from shared.exceptions import AuthenticationError
from shared.security.config import SecuritySettings, get_security_settings
from shared.security.principal import UserPrincipal


class StatelessTokenValidator:
    """
    Stateless JWT Access Token Validator.

    Design Patterns & Engineering Principles:
    - Single Responsibility Principle (SRP): Dedicated exclusively to signature verification
      and claims decoding.
    - Stateless Verification: Requires zero database lookups or inter-service network calls.
    - Defense-in-Depth: Explicitly enforces token type ("access") and presence of essential claims
      to defeat privilege escalation or token substitution attacks.
    """

    def __init__(self, settings: SecuritySettings | None = None) -> None:
        self._settings = settings or get_security_settings()

    def decode_token(self, token: str) -> dict[str, Any]:
        """
        Cryptographically decodes and validates a JWT signature and expiration.
        Raises AuthenticationError on expired signatures, invalid algorithms, or malformed tokens.
        """
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm],
                audience=self._settings.audience,
                issuer=self._settings.issuer,
            )
            if payload.get("type") != "access":
                raise AuthenticationError("Invalid token type: expected access token")
            return payload
        except jwt.ExpiredSignatureError as e:
            raise AuthenticationError("Access token has expired") from e
        except jwt.InvalidTokenError as e:
            raise AuthenticationError("Invalid or malformed access token") from e

    def validate_and_extract_principal(self, token: str) -> UserPrincipal:
        """
        Factory / Converter Method: Decodes token and builds an immutable UserPrincipal.
        """
        payload = self.decode_token(token)

        try:
            user_id = UUID(payload["sub"])
        except (KeyError, ValueError) as e:
            raise AuthenticationError("Token missing or malformed 'sub' identity claim") from e

        email = payload.get("email")
        if not email:
            raise AuthenticationError("Token missing 'email' claim")

        role = payload.get("role")
        if not role:
            raise AuthenticationError("Token missing 'role' claim")

        raw_workspace = payload.get("workspace_id")
        workspace_id: UUID | None = None
        if raw_workspace:
            try:
                workspace_id = UUID(raw_workspace)
            except ValueError as e:
                raise AuthenticationError("Token contains malformed 'workspace_id' claim") from e

        return UserPrincipal(
            id=user_id,
            email=email,
            role=role,
            workspace_id=workspace_id,
        )
