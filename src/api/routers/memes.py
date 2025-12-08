"""
Endpoints for meme generation.
Follow REST API principles and asynchronous processing.
"""

import os
from pathlib import Path

from celery.app.control import Inspect
from celery.result import AsyncResult
from fastapi import APIRouter, status
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
    MemegenRequest,
    MemegenResponse,
    TaskProgressInfo,
    TaskResponse,
    TaskStatus,
    TaskStatusResponse,
)
from src.config.logging_config import get_logger
from src.core.llm_client import OllamaClient
from src.models.meme import PREDEFINED_STYLES
from src.services.caption_service import CaptionForImageService
from src.services.memegen_service import MemeGenerator
from src.worker.celery_app import celery_app
from src.worker.tasks import generate_meme_task

logger = get_logger(__name__)
router = APIRouter(prefix="/api/memes", tags=["Memes"])
ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
model_name = os.getenv("OLLAMA_MODEL", "alibayram/smollm3")
ollama_client = OllamaClient(model_name, 30)


meme_generator = MemeGenerator(
    ollama_url=ollama_host,
    caption_service=CaptionForImageService(ollama_client),
)


@router.post(
    "/generate-template",
    response_model=MemegenResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate meme using memegen.link API",
    description=(
        "Generates a meme with random template selection and LLM-powered captions. "
        "Returns URL to the generated meme on memegen.link."
    ),
)
async def generate_meme_with_memegen(
    request: MemegenRequest,
    request_id: RequestIDDep,
    config: ConfigDep,
) -> MemegenResponse:
    """
    Generate a meme using memegen.link API with LLM captions.

    This endpoint:
    1. Randomly selects a meme template from 105+ available templates
    2. Uses LLM to generate appropriate captions based on user context
    3. Returns a URL to the generated meme

    Args:
        request: Request with context and optional parameters
        request_id: Unique request ID (DI)
        config: Application configuration (DI)

    Returns:
        MemegenResponse with URL and metadata

    Example:
        ```
        {
            "context": "Когда код работает с первого раза",
            "width": 512,
            "height": 512
        }
        ```

    Response:
        ```
        {
            "url": "https://api.memegen.link/images/drake/...",
            "template": "drake",
            "text": "Дебажить 3 часа",
        }
        ```
    """  # noqa: RUF002

    logger.info(
        "Received memegen request: context='%s', width=%d, height=%d",
        request.context,
        request.width,
        request.height,
        extra={"request_id": request_id},
    )

    try:
        # Генерируем мем с помощью MemeGenerator
        result = meme_generator.generate_meme(
            context=request.context,
            width=request.width,
            height=request.height,
        )

        logger.info(
            "Meme generated successfully: template='%s', url='%s'",
            result["template"],
            result["url"],
            extra={"request_id": request_id},
        )

        return MemegenResponse(
            url=result["url"],
            template=result["template"],
            text=result["text"],
        )

    except Exception as e:
        logger.exception(
            "Failed to generate meme: %s",
            str(e),
            extra={"request_id": request_id},
        )
        raise


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
    config: ConfigDep,
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
    config: ConfigDep,
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
async def get_meme_result(
    task_id: str,
    config: ConfigDep,
) -> FileResponse:
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

    logger.debug("Result retrieval for task", extra={"task_id": task_id})

    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == TaskStatus.SUCCESS:
        result = task_result.result
        image_path = result.get("final_image_path")

        if image_path and Path(image_path).exists():
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


@router.get("/api/tasks/stats")
async def get_tasks_stats():
    """
    Get statistics about all tasks (including PENDING).

    Returns:
        Dictionary with task counts by status
    """

    inspect = Inspect(app=celery_app)

    # Active tasks
    active = inspect.active() or {}
    active_count = sum(len(tasks) for tasks in active.values())

    # Reserved tasks (in queue)
    reserved = inspect.reserved() or {}
    reserved_count = sum(len(tasks) for tasks in reserved.values())

    # Worker statistics
    stats = inspect.stats() or {}

    return {
        "active_tasks": active_count,
        "pending_tasks": reserved_count,  # These are tasks in the queue (PENDING)
        "worker_count": len(stats),
        "workers": list(stats.keys()),
        "active": active,
        "reserved": reserved,
    }
