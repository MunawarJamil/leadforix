"""
RabbitMQ Configuration Settings using Pydantic Settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseSettings):
    rabbitmq_url: str = "amqp://leadforix:leadforix@localhost:5672/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RABBITMQ_",
        extra="ignore",
    )


@lru_cache
def get_rabbitmq_settings() -> RabbitMQSettings:
    return RabbitMQSettings()
