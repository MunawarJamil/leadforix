"""
RabbitMQ Consumer Worker for Workspace Provisioning.

Design Patterns:
- Competing Consumers / Event-Driven Architecture: Asynchronously handles 'user.registered' events.
- Idempotency & Fault Isolation: Re-delivered messages do not duplicate workspaces.
"""

import asyncio
import json
import logging
from uuid import UUID

import aio_pika

from apps.services.workspace_service.app.application.service import WorkspaceService
from apps.services.workspace_service.app.domain.roles import TenantType
from shared.database.session import get_db_session
from shared.messaging.rabbitmq import EXCHANGE_NAME, get_rabbitmq_connection

logger = logging.getLogger(__name__)

QUEUE_NAME = "workspace.user_registered.queue"
ROUTING_KEY = "user.registered"


async def process_user_registered_event(payload: dict) -> None:
    """Processes a single user.registered event inside an isolated DB session."""
    user_id = UUID(payload["user_id"])
    email = payload["email"]
    tenant_type_str = payload.get("tenant_type", "JOB_SEEKER")
    tenant_type = TenantType(tenant_type_str)

    async for session in get_db_session():
        service = WorkspaceService(session)
        workspace = await service.provision_personal_workspace(
            user_id=user_id,
            email=email,
            tenant_type=tenant_type,
        )
        logger.info(
            "Successfully provisioned workspace '%s' (id: %s) for user %s",
            workspace.name,
            workspace.id,
            user_id,
        )
        break


async def run_workspace_consumer() -> None:
    """
    Background worker loop listening for 'user.registered' events from RabbitMQ.
    """
    while True:
        try:
            logger.info("Connecting workspace consumer to RabbitMQ...")
            connection = await get_rabbitmq_connection()
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=10)

                # Declare exchange and durable queue
                exchange = await channel.declare_exchange(
                    name=EXCHANGE_NAME,
                    type=aio_pika.ExchangeType.TOPIC,
                    durable=True,
                )
                queue = await channel.declare_queue(
                    name=QUEUE_NAME,
                    durable=True,
                )
                await queue.bind(exchange, routing_key=ROUTING_KEY)

                logger.info("Workspace consumer started. Listening on queue '%s'...", QUEUE_NAME)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            try:
                                payload = json.loads(message.body.decode("utf-8"))
                                await process_user_registered_event(payload)
                            except Exception as exc:
                                logger.error("Error processing user.registered event: %s", exc, exc_info=True)

        except asyncio.CancelledError:
            logger.info("Workspace consumer task cancelled.")
            break
        except Exception as exc:
            logger.warning("RabbitMQ connection lost in workspace consumer: %s. Retrying in 5s...", exc)
            await asyncio.sleep(5)
