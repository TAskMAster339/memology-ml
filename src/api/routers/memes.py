"""
Endpoints for meme generation.
Follow REST API principles and asynchronous processing.
"""

from pathlib import Path

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse

from src.api.dependencies import ConfigDep, RequestIDDep
from src.api.exceptions import (
    ImageNotFoundException,
    InvalidStyleException,
    TaskFailedException,
    TaskNotFoundException,
    TaskStillProcessingException,
)
from src.api.schemas import (
    MemeGenerationRequest,
    MemeGenerationResult,
    TaskProgressInfo,
    TaskResponse,
    TaskStatus,
    TaskStatusResponse,
)
from src.config.logging_config import get_logger
from src.models.meme import PREDEFINED_STYLES
from src.worker.celery_app import celery_app
from src.worker.tasks import generate_meme_task

logger = get_logger(__name__)
router = APIRouter(prefix="/api/memes", tags=["Memes"])


@router.post(
    "/generate",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create a meme generation task",
    description=(
        "Creates a task for meme generation and returns a task_id for tracking"
    ),
)
async def generate_meme(
    request: MemeGenerationRequest,
    request_id: RequestIDDep,
    config: Depends | None = None,
) -> TaskResponse:
    """
    Create a meme generation task.

    Args:
        request: Request with meme description
        config: Application configuration (DI)
        request_id: Unique request ID (DI)

    Returns:
        Information about the created task with task_id

    Raises:
        InvalidStyleException: If a non-existent style is specified
    """
    if config is None:
        config = Depends(ConfigDep)

    logger.info(
        "Received meme generation request: input='%s', style='%s'",
        request.user_input,
        request.style,
        extra={"request_id": request_id},
    )

    # Validate style if specified
    if request.style:
        available_styles = [s.name for s in PREDEFINED_STYLES]
        if request.style not in available_styles:
            logger.warning(
                "Invalid style requested: %s",
                request.style,
                extra={"request_id": request_id},
            )
            raise InvalidStyleException(request.style, available_styles)

    # Send task to Celery
    task = generate_meme_task.apply_async(
        args=[request.user_input, request.style],
        task_id=request_id,  # Use request_id as task_id for tracing
    )

    logger.info("Task created", extra={"request_id": request_id, "task_id": task.id})

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message="Task added to queue. Use task_id to check status.",
    )


@router.get(
    "/styles",
    response_model=list[dict],
    summary="Get a list of available styles",
    description="Returns all available meme visualization styles",
)
async def get_available_styles() -> list[dict]:
    """
    Get a list of all available styles.

    Returns:
        List of styles with names and descriptions
    """
    logger.debug("Available styles requested")

    return [
        {"name": style.name, "description": style.description}
        for style in PREDEFINED_STYLES
    ]


@router.get(
    "/task/{task_id}",
    response_model=TaskStatusResponse,
    summary="Get task status",
    description="Check the current status of a meme generation task",
)
async def get_task_status(
    task_id: str,
    config: Depends | None = None,
) -> TaskStatusResponse:
    """
    Get detailed task status.

    Args:
        task_id: Task UUID
        config: Application configuration (DI)

    Returns:
        Detailed information about the task status

    Raises:
        TaskNotFoundException: If the task is not found
    """
    if config is None:
        config = Depends(ConfigDep)

    logger.debug("Status check for task", extra={"task_id": task_id})

    task_result = AsyncResult(task_id, app=celery_app)

    # Form response based on status
    response_data = {
        "task_id": task_id,
        "status": TaskStatus(task_result.state),
    }

    if task_result.state == TaskStatus.PENDING:
        response_data["progress"] = TaskProgressInfo(
            current=0,
            total=4,
            status="Task is waiting in the queue",
        )
        logger.debug("Task is PENDING", extra={"task_id": task_id})

    elif task_result.state == TaskStatus.STARTED:
        # Extract progress information
        info = task_result.info if task_result.info else {}
        response_data["progress"] = TaskProgressInfo(
            current=info.get("current", 1),
            total=info.get("total", 4),
            status=info.get("status", "Generation started..."),
        )
        logger.debug("Task is STARTED", extra={"task_id": task_id, "info": info})

    elif task_result.state == TaskStatus.SUCCESS:
        result_data = task_result.result
        response_data["result"] = MemeGenerationResult(**result_data)
        logger.info("Task completed successfully", extra={"task_id": task_id})

    elif task_result.state == TaskStatus.FAILURE:
        error_msg = str(task_result.info)
        response_data["error"] = error_msg
        logger.error("Task failed", extra={"task_id": task_id, "error": error_msg})

    elif task_result.state == TaskStatus.RETRY:
        info = task_result.info if task_result.info else {}
        response_data["progress"] = TaskProgressInfo(
            current=0,
            total=4,
            status="Retrying generation...",
        )
        logger.warning("Task is retrying", extra={"task_id": task_id})

    return TaskStatusResponse(**response_data)


@router.get(
    "/task/{task_id}/result",
    response_class=FileResponse,
    summary="Get the generated meme",
    description="Download the generated meme file (only for completed tasks)",
)
async def get_meme_result(task_id: str, config: Depends | None = None) -> FileResponse:
    """
    Get the generated meme file.

    Args:
        task_id: Task UUID
        config: Application configuration (DI)

    Returns:
        Image file

    Raises:
        TaskStillProcessingException: If the task is still processing
        TaskFailedException: If the task failed
        ImageNotFoundException: If the image file is not found
    """
    if config is None:
        config = Depends(ConfigDep)

    logger.debug("Result retrieval for task", extra={"task_id": task_id})

    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == TaskStatus.SUCCESS:
        result = task_result.result
        image_path = result.get("final_image_path")

        if image_path and Path.exists(image_path):
            logger.info(
                "Returning image for task",
                extra={"task_id": task_id, "image_path": image_path},
            )
            return FileResponse(
                image_path,
                filename=Path(image_path).name,
                headers={
                    "X-Task-ID": task_id,
                    "X-Generation-ID": result.get("generation_id", "unknown"),
                },
            )
        logger.error(
            "Image file not found for task",
            extra={"task_id": task_id, "image_path": image_path},
        )
        raise ImageNotFoundException(image_path or "unknown")

    if task_result.state in [
        TaskStatus.PENDING,
        TaskStatus.STARTED,
        TaskStatus.RETRY,
    ]:
        logger.debug(
            "Task still processing",
            extra={"task_id": task_id, "state": task_result.state},
        )
        raise TaskStillProcessingException(task_id)

    if task_result.state == TaskStatus.FAILURE:
        error_msg = str(task_result.info)
        logger.error(
            "Cannot return result for failed task",
            extra={"task_id": task_id, "error": error_msg},
        )
        raise TaskFailedException(task_id, error_msg)

    logger.warning(
        "Unknown task state",
        extra={"task_id": task_id, "state": task_result.state},
    )
    raise TaskNotFoundException(task_id)
