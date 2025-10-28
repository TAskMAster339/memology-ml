"""
Celery application configuration.
Follows OOP principles and distributed task queue setup.
"""

import os
from typing import ClassVar

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

from src.config.logging_config import LoggingConfigurator, get_logger

# Initialize logging
LoggingConfigurator.configure()
logger = get_logger(__name__)


class CeleryConfig:
    """
    Celery configuration.
    Centralized management of worker settings.
    Follows new Celery 5.x naming conventions (without CELERY_ prefix in class).
    """

    # Broker and Backend (NEW NAMES for Celery 5.x)
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/0",
    )
    broker_connection_retry_on_startup = True

    # Serialization
    task_serializer = "json"
    accept_content: ClassVar[list[str]] = ["json"]
    result_serializer = "json"

    # Timezone
    timezone = "UTC"
    enable_utc = True

    # Task execution
    task_time_limit = int(
        os.getenv("CELERY_TASK_TIME_LIMIT", "1800"),
    )  # 30 minutes (hard limit)
    task_soft_time_limit = int(
        os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "1500"),
    )  # 25 minutes (soft limit) - time for graceful shutdown

    # Worker settings
    worker_prefetch_multiplier = 1  # Important for GPU tasks - one task at a time
    worker_max_tasks_per_child = 10  # Restart worker after 10 tasks
    # Task execution - INCREASED for handling long operations (meme generation)

    # Task acknowledgement
    task_acks_late = True  # Acknowledge after execution
    task_reject_on_worker_lost = True  # Reject task if worker crashes

    # Result backend settings
    result_expires = 3600  # Results are stored for 1 hour
    result_persistent = True  # Persistent result storage

    # Retry settings
    task_publish_retry = True
    task_publish_retry_policy: ClassVar[dict] = {
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 0.2,
    }

    # Queue configuration (optional)
    task_default_queue = "default"
    task_default_exchange = "default"
    task_default_routing_key = "default"

    # Priority queues can be configured
    task_queues = (
        Queue("default", Exchange("default"), routing_key="default", priority=5),
        Queue(
            "high_priority",
            Exchange("high_priority"),
            routing_key="high_priority",
            priority=10,
        ),
    )
    # ===== CELERY BEAT (Periodic Tasks) Configuration =====
    beat_schedule: ClassVar[dict] = {
        # Cleanup old meme files every day at 6:00 AM UTC
        "cleanup-old-memes": {
            "task": "src.worker.tasks.cleanup_old_files",
            "schedule": crontab(hour=6, minute=0),  # Every day at 6:00 AM UTC
            "args": (1,),  # Delete files older than 1 day
            "options": {
                "queue": "default",
            },
        },
    }


# Create Celery application
celery_app = Celery(
    "memology_worker",
    broker=CeleryConfig.broker_url,
    backend=CeleryConfig.result_backend,
    include=["src.worker.tasks"],
)

# Apply configuration
celery_app.config_from_object(CeleryConfig)

logger.info(
    "Celery app configured with broker",
    extra={"broker_url": CeleryConfig.broker_url},
)
logger.info(
    f"Celery Beat schedule configured with "  # noqa: G004
    f"{len(CeleryConfig.beat_schedule)} periodic tasks",
)
