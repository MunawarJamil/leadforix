"""
Central Celery application configuration and periodic task scheduler (Celery Beat).

Design Patterns:
- Centralized Configuration: Shared broker and result backend settings across workers.
- Declarative Scheduler: Cron-style periodic task dispatching (Celery Beat).
"""

import os
from celery import Celery
from celery.schedules import crontab

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "leadforix_worker",
    broker=broker_url,
    backend=result_backend,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    imports=[
        "apps.services.lead_service.app.infrastructure.tasks",
    ],
    beat_schedule={
        "discover_leads_every_6_hours": {
            "task": "lead_service.discover_leads",
            "schedule": crontab(minute=0, hour="*/6"),  # At minute 0 past every 6th hour
            "kwargs": {
                "hn_limit": 100,
                "remotive_limit": 100,
                "remotive_category": "software-dev",
                "save_only_qualified": False,
            },
        },
    },
)


@celery_app.task(name="health_check_task")
def health_check_task():
    return {"status": "ok", "worker": "leadforix_worker"}
