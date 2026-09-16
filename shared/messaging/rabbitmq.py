"""
RabbitMQ Asynchronous Messaging Infrastructure using aio-pika.

Design Patterns:
- Robust Connection / Circuit Resilience: Auto-reconnects on network drops.
- Publisher Pattern: Publishes JSON events to a durable topic exchange.
"""

import json
from typing import Any
import aio_pika
from shared.config.rabbitmq import get_rabbitmq_settings


EXCHANGE_NAME = "leadforix.events"


async def get_rabbitmq_connection() -> aio_pika.abc.AbstractRobustConnection:
    """Creates a resilient, auto-reconnecting AMQP connection."""
    settings = get_rabbitmq_settings()
    return await aio_pika.connect_robust(settings.rabbitmq_url)


async def publish_event(
    routing_key: str,
    payload: dict[str, Any],
    exchange_name: str = EXCHANGE_NAME,
) -> None:
    """
    Publishes an event payload to a durable Topic Exchange.
    """
    connection = await get_rabbitmq_connection()
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            name=exchange_name,
            type=aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        message_body = json.dumps(payload, default=str).encode("utf-8")
        message = aio_pika.Message(
            body=message_body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Disk-persisted for reliability
            content_type="application/json",
        )
        await exchange.publish(message, routing_key=routing_key)
