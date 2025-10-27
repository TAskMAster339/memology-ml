"""
Celery tasks for meme generation.
Follows OOP principles and asynchronous processing.
"""

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from celery import Task

from src.config.logging_config import get_logger
from src.models.meme import PREDEFINED_STYLES
from src.worker.celery_app import celery_app
from src.worker.factory import ServiceFactory

logger = get_logger(__name__)


class MemeGenerationTask(Task):
    """
    Base class for meme generation tasks.
    Implements error handling and lifecycle hooks.
    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Callback for task failure.

        Args:
            exc: Exception
            task_id: Task ID
            args: Positional arguments
            kwargs: Keyword arguments
            einfo: Error information
        """
        logger.error(
            "Task %(task_id)s failed with exception: %(exception)s",
            {"task_id": task_id, "exception": exc},
            exc_info=einfo,
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """
        Callback for successful task completion.

        Args:
            retval: Return value
            task_id: Task ID
            args: Positional arguments
            kwargs: Keyword arguments
        """
        logger.info(
            "Task %(task_id)s completed successfully",
            extra={"task_id": task_id},
        )
        super().on_success(retval, task_id, args, kwargs)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        Callback for task retry.

        Args:
            exc: Exception
            task_id: Task ID
            args: Positional arguments
            kwargs: Keyword arguments
            einfo: Error information
        """
        logger.warning(
            "Task is being retried due to: %(exception)s",
            extra={"exception": exc},
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)


@celery_app.task(
    base=MemeGenerationTask,
    bind=True,
    name="src.worker.tasks.generate_meme_task",
    autoretry_for=(Exception,),
    retry_kwargs={
        "max_retries": 2,
        "countdown": 60,  # 60 seconds between retries
    },
    retry_backoff=True,
    retry_backoff_max=300,  # Maximum 5 minutes
    retry_jitter=True,
)
def generate_meme_task(
    self,
    user_input: str,
    style_name: str | None = None,
) -> dict[str, Any]:
    """
    Celery task for meme generation.

    Args:
        self: Task instance (bind=True)
        user_input: Text prompt from the user
        style_name: Style name (optional)

    Returns:
        Dictionary with information about the generation result

    Raises:
        Exception: On generation errors (with automatic retry)
    """
    task_id = self.request.id
    logger.info("Starting meme generation task", extra={"task_id": task_id})
    logger.info(
        "Input: '%(user_input)s', Style: '%(style_name)s'",
        extra={"task_id": task_id, "user_input": user_input, "style_name": style_name},
    )

    try:
        # Step 1: Initialization
        self.update_state(
            state="STARTED",
            meta={"current": 0, "total": 4, "status": "Initializing services..."},
        )

        meme_service = ServiceFactory.create_meme_service()
        logger.debug("MemeService initialized", extra={"task_id": task_id})

        # Step 2: Style selection
        self.update_state(
            state="STARTED",
            meta={
                "current": 1,
                "total": 4,
                "status": "Selecting visualization style...",
            },
        )

        if style_name:
            style = next((s for s in PREDEFINED_STYLES if s.name == style_name), None)
            if style is None:
                logger.warning(
                    "[%(task_id)s] Style '%(style_name)s' not found, using random",
                    extra={"task_id": task_id, "style_name": style_name},
                )
                style = random.choice(PREDEFINED_STYLES)
        else:
            style = random.choice(PREDEFINED_STYLES)

        logger.info(
            "[%(task_id)s] Selected style: %(style_name)s",
            extra={"task_id": task_id, "style_name": style.name},
        )

        # Step 3: Prompt generation
        self.update_state(
            state="STARTED",
            meta={
                "current": 2,
                "total": 4,
                "status": f"Generating prompt for style: {style.name}",
            },
        )

        # Step 4: Meme generation (main work)
        self.update_state(
            state="STARTED",
            meta={
                "current": 3,
                "total": 4,
                "status": "Generating image (this may take ~5 minutes)...",
            },
        )

        result = meme_service.generate_meme(user_input, style=style)

        if not result.success:
            error_msg = result.error_message or "Unknown error"
            logger.error(
                "Generation failed: %(error_msg)s",
                extra={"task_id": task_id, "error_msg": error_msg},
            )
            raise Exception(f"Generation error: {error_msg}")  # noqa: TRY002, TRY003, TRY301

        # Step 5: Finalization
        self.update_state(
            state="STARTED",
            meta={"current": 4, "total": 4, "status": "Finalizing..."},
        )

        logger.info(
            "[%(task_id)s] Meme generated successfully: "
            "id=%(generation_id)s, path=%(final_image_path)s",
            extra={
                "task_id": task_id,
                "generation_id": result.generation_id,
                "final_image_path": result.final_image_path,
            },
        )

        # Form the result
        return {
            "success": True,
            "final_image_path": result.final_image_path,
            "caption": result.caption,
            "style": style.name,
            "user_input": user_input,
            "generation_id": result.generation_id,
            "generated_at": datetime.now(tz=datetime.timezone.utc).isoformat(),
        }

    except Exception:
        logger.exception(
            "Error in meme generation task",
            extra={"task_id": task_id},
        )
        raise  # Celery automatically retry


# Additional task for cleaning up old files (optional)
@celery_app.task(name="src.worker.tasks.cleanup_old_files")
def cleanup_old_files_task(days_old: int = 7) -> dict[str, int] | None:
    """
    Task for cleaning up old generated files.

    Args:
        days_old: Delete files older than N days
    """

    logger.info(
        "Starting cleanup of files older than %(days_old)s days",
        extra={"days_old": days_old},
    )

    output_dir = Path("generated_images")
    if not output_dir.exists():
        return None

    cutoff_time = datetime.now(tz=datetime.timezone.utc) - timedelta(days=days_old)
    deleted_count = 0

    for file_path in output_dir.glob("*.jpg"):
        file_mtime = datetime.fromtimestamp(
            file_path.stat().st_mtime,
            tz=datetime.timezone.utc,
        )
        if file_mtime < cutoff_time:
            try:
                file_path.unlink()
                deleted_count += 1
                logger.debug(
                    "Deleted old file: %(file_path)s",
                    extra={"file_path": str(file_path)},
                )
            except Exception as e:
                logger.exception(
                    "Failed to delete %(file_path)s: %(error_msg)s",
                    extra={"file_path": str(file_path), "error_msg": str(e)},
                )

    logger.info(
        "Cleanup completed: %(deleted_count)s files deleted",
        extra={"deleted_count": deleted_count},
    )
    return {"deleted_count": deleted_count}
