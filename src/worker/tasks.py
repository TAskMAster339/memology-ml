"""
Celery tasks for meme generation.
Follows OOP principles and asynchronous processing.
"""

import random
from datetime import datetime, timedelta, timezone
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
            einfo: Error information"""
        logger.error(
            f"Task {task_id} failed with exception: {exc}",  # noqa: G004
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
            f"Task {task_id} completed successfully",  # noqa: G004
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
            einfo: Error information"""
        logger.warning(
            f"Task is being retried due to: {exc}",  # noqa: G004
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
    logger.info(f"Starting meme generation task - task_id: {task_id}")  # noqa: G004
    logger.info(
        f"Input: '{user_input}', Style: '{style_name}' - task_id: {task_id}",  # noqa: G004
    )

    try:
        # Step 1: Initialization
        self.update_state(
            state="STARTED",
            meta={"current": 0, "total": 4, "status": "Initializing services..."},
        )
        meme_service = ServiceFactory.create_meme_service()
        logger.debug(f"MemeService initialized - task_id: {task_id}")  # noqa: G004

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
                    f"[{task_id}] Style '{style_name}' not found, using random",  # noqa: G004
                )
                style = random.choice(PREDEFINED_STYLES)
        else:
            style = random.choice(PREDEFINED_STYLES)
        logger.info(
            f"[{task_id}] Selected style: {style.name}",  # noqa: G004
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
                f"Generation failed: {error_msg} - task_id: {task_id}",  # noqa: G004
            )
            raise Exception(f"Generation error: {error_msg}")  # noqa: TRY002, TRY003, TRY301

        # Step 5: Finalization
        self.update_state(
            state="STARTED",
            meta={"current": 4, "total": 4, "status": "Finalizing..."},
        )
        logger.info(
            f"[{task_id}] Meme generated successfully: "  # noqa: G004
            f"id={result.request.request_id}, path={result.final_image_path}",
        )

        # Form the result
        return {
            "success": True,
            "final_image_path": result.final_image_path,
            "caption": result.caption,
            "style": style.name,
            "user_input": user_input,
            "generation_id": result.request.request_id,
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }

    except Exception:
        logger.exception(
            f"Error in meme generation task - task_id: {task_id}",  # noqa: G004
        )
        raise  # Celery automatically retry


# Additional task for cleaning up old files (optional)
@celery_app.task(name="src.worker.tasks.cleanup_old_files")
def cleanup_old_files_task(days_old: int = 1) -> dict[str, int] | None:
    """
    Task for cleaning up old generated files.

    Args:
        days_old: Delete files older than N days
    """
    logger.info(
        f"Starting cleanup of files older than {days_old} days",  # noqa: G004
    )

    output_dir = Path("generated_images")
    if not output_dir.exists():
        return None

    cutoff_time = datetime.now(tz=timezone.utc) - timedelta(days=days_old)
    deleted_count = 0

    for file_path in output_dir.glob("*.png"):
        file_mtime = datetime.fromtimestamp(
            file_path.stat().st_mtime,
            tz=timezone.utc,
        )
        if file_mtime < cutoff_time:
            try:
                file_path.unlink()
                deleted_count += 1
                logger.debug(
                    f"Deleted old file: {file_path}",  # noqa: G004
                )
            except Exception as e:
                logger.exception(
                    f"Failed to delete {file_path}: {e}",  # noqa: G004, TRY401
                )
    logger.info(
        f"Cleanup completed: {deleted_count} files deleted",  # noqa: G004
    )
    return {"deleted_count": deleted_count}
