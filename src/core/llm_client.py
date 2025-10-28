"""
Abstraction for working with language models via Ollama.
"""

import os
import threading
from abc import ABC, abstractmethod

import ollama

from src.utils.logger import LoggerManager


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        timeout: int | None = None,
    ) -> str:
        """
        Generates a response based on messages.
        Args:
            messages: List of messages in the format [{"role": "...", "content": "..."}]
            timeout: Execution timeout in seconds
        Returns:
            Generated text
        """


class OllamaClient(BaseLLMClient):
    """Client for interacting with Ollama LLM."""

    def __init__(self, model: str, default_timeout: int = 15):
        """
        Initializes the Ollama client.

        Args:
            model: Model name (e.g., "llama3.2:3b")
            default_timeout: Default timeout in seconds
        """
        self.model = model
        self.default_timeout = default_timeout
        self.logger = LoggerManager.get_logger(__name__)

        # Configure ollama client with custom host
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=ollama_host)  # ← Create client with host

    def generate(
        self,
        messages: list[dict[str, str]],
        timeout: int | None = None,
    ) -> str:
        """
        Generates a response via Ollama with timeout support.

        Args:
            messages: List of messages
            timeout: Timeout (if None, uses default_timeout)

        Returns:
            Generated text

        Raises:
            TimeoutError: If timeout is exceeded
            Exception: For other generation errors
        """
        timeout = timeout or self.default_timeout

        try:
            response = self._run_with_timeout(
                lambda: self.client.chat(model=self.model, messages=messages),
                timeout,
            )
            return response["message"]["content"]
        except TimeoutError:
            self.logger.exception("Timeout error during LLM generation")
            raise
        except Exception as e:
            self.logger.exception(f"Error during LLM generation: {e}")  # noqa: G004, TRY401
            raise

    def _run_with_timeout(self, func, timeout: int):
        """
        Executes a function with a time limit.

        Args:
            func: Function to execute
            timeout: Maximum execution time in seconds

        Returns:
            Result of the function execution

        Raises:
            TimeoutError: If the function did not finish in time
        """
        result = [None]
        exception = [None]

        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            raise TimeoutError(f"Function execution exceeded {timeout} seconds")  # noqa: TRY003

        if exception[0]:
            raise exception[0]

        return result[0]
