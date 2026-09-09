from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """
    Authentication & Cryptographic Configuration.

    Design Pattern:
    - Encapsulation: Groups and validates all security-related configuration in one class.
    - Configuration Pattern: Uses pydantic-settings to read from environment variables or .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # JWT Configuration
    secret_key: str = Field(
        default="leadforix-super-secret-change-in-production-jwt-key-32chars",
        alias="JWT_SECRET_KEY",
        description="Cryptographic secret key used to sign and verify HMAC-SHA256 JWT tokens",
    )
    algorithm: str = Field(
        default="HS256",
        alias="JWT_ALGORITHM",
        description="Signature algorithm for JWT tokens",
    )
    issuer: str = Field(
        default="leadforix-auth",
        alias="JWT_ISSUER",
        description="Expected JWT token issuer",
    )
    audience: str = Field(
        default="leadforix-api",
        alias="JWT_AUDIENCE",
        description="Expected JWT token audience",
    )
    access_token_expire_minutes: int = Field(
        default=15,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Lifetime of short-lived access tokens in minutes",
    )
    refresh_token_expire_days: int = Field(
        default=7,
        alias="REFRESH_TOKEN_EXPIRE_DAYS",
        description="Lifetime of long-lived refresh tokens in days",
    )


@lru_cache
def get_auth_settings() -> AuthSettings:
    """
    Design Pattern: Singleton Provider
    Uses Python's @lru_cache to ensure AuthSettings is instantiated and validated
    only once during runtime, preventing repeated disk/environment reads.
    """
    return AuthSettings()
