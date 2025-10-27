"""
Celery application configuration.
Follows OOP principles and distributed task queue setup.
"""

import os
from typing import ClassVar

from celery import Celery
from kombu import Exchange, Queue

from src.config.logging_config import LoggingConfigurator, get_logger

# Initialize logging
LoggingConfigurator.configure()
logger = get_logger(__name__)


class CeleryConfig:
    """
    Celery configuration.
    Centralized management of worker settings.
    """

    # Broker and Backend
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/0",
    )

    # Serialization
    task_serializer = "json"

    accept_content: ClassVar[list[str]] = ["json"]
    result_serializer = "json"

    # Timezone
    timezone = "UTC"
    enable_utc = True

    # Task execution
    task_time_limit = int(os.getenv("CELERY_TASK_TIME_LIMIT", "600"))  # 10 minutes
    task_soft_time_limit = int(
        os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "540"),
    )  # 9 minutes

    # Worker settings
    worker_prefetch_multiplier = 1  # Important for GPU tasks - one task at a time
    worker_max_tasks_per_child = 10  # Restart worker after 10 tasks

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


# Create Celery application
celery_app = Celery(
    "memology_worker",
    broker=CeleryConfig.CELERY_BROKER_URL,
    backend=CeleryConfig.CELERY_RESULT_BACKEND,
    include=["src.worker.tasks"],
)

# Apply configuration
celery_app.config_from_object(CeleryConfig)

logger.info(
    "Celery app configured with broker",
    extra={"broker_url": CeleryConfig.CELERY_BROKER_URL},
)
