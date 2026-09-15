from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """
    Agent Service & LLM Configuration.

    Design Patterns:
    - Encapsulation: Consolidates AI model parameters, timeout controls, and tracing settings.
    - Configuration Pattern: Strongly-typed Pydantic settings read from environment/.env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Provider Configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        alias="OPENAI_API_KEY",
        description="API key for OpenAI-compatible chat model endpoints",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        alias="OPENAI_MODEL",
        description="Default chat model used for evaluation and drafting",
    )
    openai_temperature: float = Field(
        default=0.2,
        alias="OPENAI_TEMPERATURE",
        description="Sampling temperature for deterministic agent reasoning",
    )
    request_timeout_seconds: float = Field(
        default=30.0,
        alias="AGENT_REQUEST_TIMEOUT_SECONDS",
        description="HTTP client timeout for LLM provider API invocations",
    )
    max_retries: int = Field(
        default=3,
        alias="AGENT_MAX_RETRIES",
        description="Maximum retry attempts on transient LLM provider rate limits or timeouts",
    )

    # LangSmith Observability & Tracing
    langsmith_tracing: bool = Field(
        default=False,
        alias="LANGSMITH_TRACING",
        description="Toggle for distributed LangSmith agent trace logging",
    )
    langsmith_api_key: Optional[str] = Field(
        default=None,
        alias="LANGSMITH_API_KEY",
        description="LangSmith API key for remote observability telemetry",
    )
    langsmith_project: str = Field(
        default="leadforix-agents",
        alias="LANGSMITH_PROJECT",
        description="Target LangSmith telemetry project namespace",
    )
    langsmith_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        alias="LANGSMITH_ENDPOINT",
        description="LangSmith telemetry ingestion endpoint",
    )


@lru_cache
def get_agent_settings() -> AgentSettings:
    """
    Design Pattern: Singleton Provider
    Cached singleton factory returning validated AgentSettings instance.
    """
    return AgentSettings()
