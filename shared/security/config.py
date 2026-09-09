from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    """
    Cryptographic Security Configuration for Microservices.

    Design Patterns:
    - Configuration Pattern: Uses pydantic-settings to read from environment variables or .env.
    - Uniform Secret Distribution: Ensures all microservices verify JWTs against the identical
      HMAC secret key and signature algorithm.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = Field(
        default="leadforix-super-secret-change-in-production-jwt-key-32chars",
        alias="JWT_SECRET_KEY",
        description="Shared secret key used to verify HMAC-SHA256 JWT tokens across all services",
    )
    algorithm: str = Field(
        default="HS256",
        alias="JWT_ALGORITHM",
        description="Cryptographic signature algorithm for JWT tokens",
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


@lru_cache
def get_security_settings() -> SecuritySettings:
    """
    Design Pattern: Singleton Provider
    Python's @lru_cache ensures configuration is parsed and validated once per process lifetime.
    """
    return SecuritySettings()
