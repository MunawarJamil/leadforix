from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL Database configuration supporting asyncpg and connection pooling."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://leadforix:leadforix@localhost:5432/leadforix",
        alias="DATABASE_URL",
        description="Async PostgreSQL connection string",
    )

    # Connection Pool Settings: Sized conservatively for multi-microservice architecture
    # (8 services * workers) to prevent exhausting PostgreSQL's max_connections limit.
    pool_size: int = Field(
        default=5,
        alias="DB_POOL_SIZE",
        description="Base connection pool size per service process",
    )
    max_overflow: int = Field(
        default=5,
        alias="DB_MAX_OVERFLOW",
        description="Maximum transient overflow connections per process",
    )
    pool_timeout: float = Field(
        default=30.0,
        alias="DB_POOL_TIMEOUT",
        description="Connection acquisition timeout in seconds",
    )

    pool_recycle: int = Field(
        default=1800, alias="DB_POOL_RECYCLE", description="Connection recycle interval in seconds"
    )
    pool_pre_ping: bool = Field(
        default=True,
        alias="DB_POOL_PRE_PING",
        description="Check connection health before issuing queries",
    )
    echo_sql: bool = Field(
        default=False, alias="DB_ECHO_SQL", description="Log generated SQL statements"
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def ensure_asyncpg_driver(cls, value: str) -> str:
        """Ensure the URL dialect uses asyncpg for SQLAlchemy async engine."""
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        return value


@lru_cache
def get_db_settings() -> DatabaseSettings:
    """Cached singleton provider for database settings."""
    return DatabaseSettings()
