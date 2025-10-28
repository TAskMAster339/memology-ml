"""
Custom exceptions for the API.
Follow OOP and error handling principles.
"""

from fastapi import HTTPException, status


class MemeAPIException(HTTPException):
    """Base exception for Meme API."""

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class TaskNotFoundException(MemeAPIException):
    """Task not found."""

    def __init__(self, task_id: str):
        super().__init__(
            detail=f"Task with ID {task_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="TASK_NOT_FOUND",
        )


class TaskStillProcessingException(MemeAPIException):
    """Task is still processing."""

    def __init__(self, task_id: str):
        super().__init__(
            detail=f"Task {task_id} is still processing",
            status_code=status.HTTP_202_ACCEPTED,
            error_code="TASK_PROCESSING",
        )


class TaskFailedException(MemeAPIException):
    """Task failed with an error."""

    def __init__(self, task_id: str, error_message: str):
        super().__init__(
            detail=f"Task {task_id} failed with an error: {error_message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="TASK_FAILED",
        )


class ImageNotFoundException(MemeAPIException):
    """Image file not found."""

    def __init__(self, image_path: str):
        super().__init__(
            detail=f"Image file not found: {image_path}",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="IMAGE_NOT_FOUND",
        )


class InvalidStyleException(MemeAPIException):
    """Specified style does not exist."""

    def __init__(self, style: str, available_styles: list):
        super().__init__(
            detail=(
                f"Style '{style}' not found. "
                f"Available styles: {', '.join(available_styles)}"
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_STYLE",
        )


class ServiceUnavailableException(MemeAPIException):
    """External service unavailable (Ollama, Stable Diffusion)."""

    def __init__(self, service_name: str):
        super().__init__(
            detail=f"Service {service_name} unavailable. Try again later.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
        )
