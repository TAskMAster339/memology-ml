"""
Health check endpoints for monitoring the service status.
Implements comprehensive health checks for external dependencies:
- Redis (message broker)
- Ollama (LLM service)
- Stable Diffusion WebUI (image generation service)
"""

import asyncio
from datetime import datetime, timezone
from typing import Any

import aiohttp
from fastapi import APIRouter, Depends, Response, status
from redis import asyncio as aioredis

from src.api.dependencies import ConfigDep
from src.api.schemas import HealthResponse
from src.config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


class ServiceHealthChecker:
    """
    Class for checking the health of external services.
    Follows OOP principles and encapsulates health check logic.
    """

    def __init__(self, config):
        """
        Initialize the health checker with configuration.

        Args:
            config: Application configuration with service URLs
        """
        self.config = config
        self.timeout = 5  # seconds

    async def check_redis(self) -> dict[str, Any]:
        """
        Check Redis connection and availability.

        Returns:
            Dictionary with status and details
        """
        try:
            redis_url = self.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0")

            # Create Redis client
            redis_client = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

            # Try to ping Redis
            await asyncio.wait_for(redis_client.ping(), timeout=self.timeout)

            # Get some info
            info = await redis_client.info("server")

            await redis_client.close()

            return {
                "status": "healthy",
                "message": "Redis is available",
                "details": {
                    "version": info.get("redis_version", "unknown"),
                    "uptime_seconds": info.get("uptime_in_seconds", 0),
                },
            }
        except asyncio.TimeoutError:
            logger.exception("Redis health check timed out")
            return {
                "status": "unhealthy",
                "message": "Redis connection timeout",
                "details": {},
            }
        except Exception as e:
            logger.exception("Redis health check failed")
            return {
                "status": "unhealthy",
                "message": f"Redis check failed: {e!r}",
                "details": {},
            }

    async def check_ollama(self) -> dict[str, Any]:
        """
        Check Ollama API availability.

        Returns:
            Dictionary with status and details
        """
        try:
            ollama_url = self.config.get("OLLAMA_BASE_URL", "http://localhost:11434")

            async with (
                aiohttp.ClientSession() as session,
                asyncio.wait_for(
                    session.get(f"{ollama_url}/api/tags"),
                    timeout=self.timeout,
                ) as response,
            ):
                if response.status == status.HTTP_200_OK:
                    data = await response.json()
                    models = data.get("models", [])
                    model_names = [m.get("name", "unknown") for m in models]

                    return {
                        "status": "healthy",
                        "message": "Ollama is available",
                        "details": {
                            "models_count": len(models),
                            "available_models": model_names[:3],  # First 3 models
                        },
                    }
                return {
                    "status": "unhealthy",
                    "message": f"Ollama returned status {response.status}",
                    "details": {},
                }
        except asyncio.TimeoutError:
            logger.exception("Ollama health check timed out")
            return {
                "status": "unhealthy",
                "message": "Ollama connection timeout",
                "details": {},
            }
        except Exception as e:
            logger.exception("Ollama health check failed")
            return {
                "status": "unhealthy",
                "message": f"Ollama check failed: {e!s}",
                "details": {},
            }

    async def check_stable_diffusion(self) -> dict[str, Any]:
        """
        Check Stable Diffusion WebUI API availability.

        Returns:
            Dictionary with status and details
        """
        try:
            sd_url = self.config.get("SD_BASE_URL", "http://127.0.0.1:7860")

            async with (
                aiohttp.ClientSession() as session,
                asyncio.wait_for(
                    session.get(f"{sd_url}/sdapi/v1/options"),
                    timeout=self.timeout,
                ) as response,
            ):
                # Try to get SD config
                if response.status == status.HTTP_200_OK:
                    data = await response.json()

                    return {
                        "status": "healthy",
                        "message": "Stable Diffusion WebUI is available",
                        "details": {
                            "model": data.get("sd_model_checkpoint", "unknown"),
                        },
                    }
                return {
                    "status": "unhealthy",
                    "message": f"SD WebUI returned status {response.status}",
                    "details": {},
                }
        except asyncio.TimeoutError:
            logger.exception("Stable Diffusion health check timed out")
            return {
                "status": "unhealthy",
                "message": "Stable Diffusion connection timeout",
                "details": {},
            }
        except Exception as e:
            logger.exception("Stable Diffusion health check failed")
            return {
                "status": "unhealthy",
                "message": f"SD WebUI check failed: {e!s}",
                "details": {},
            }

    async def check_all_services(self) -> dict[str, Any]:
        """
        Check all external services in parallel.

        Returns:
            Dictionary with results for all services
        """
        results = await asyncio.gather(
            self.check_redis(),
            self.check_ollama(),
            self.check_stable_diffusion(),
            return_exceptions=True,
        )

        return {
            "redis": results[0]
            if not isinstance(results[0], Exception)
            else {"status": "unhealthy", "message": str(results[0]), "details": {}},
            "ollama": results[1]
            if not isinstance(results[1], Exception)
            else {"status": "unhealthy", "message": str(results[1]), "details": {}},
            "stable_diffusion": results[2]
            if not isinstance(results[2], Exception)
            else {"status": "unhealthy", "message": str(results[2]), "details": {}},
        }


@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse, include_in_schema=False)
async def health_check(config: Depends | None = None) -> HealthResponse:
    """
    Basic health check endpoint (liveness probe).
    Returns OK if the API server itself is running.
    Does not check external dependencies.

    Returns:
        Information about the service status
    """
    if config is None:
        config = Depends(ConfigDep)

    logger.debug("Health check requested")

    return HealthResponse(
        status="healthy",
        service="memology-ml-api",
        version="1.0.0",
        timestamp=datetime.now(tz=timezone.utc),
    )


@router.get("/ready", response_model=dict)
async def readiness_check(
    response: Response,
    config: Depends | None = None,
) -> dict[str, Any]:
    """
    Comprehensive readiness check endpoint.
    Checks availability of all external services (Redis, Ollama, Stable Diffusion).

    Returns HTTP 200 if all services are healthy.
    Returns HTTP 503 if any service is unhealthy.

    Args:
        response: FastAPI Response object to set status code
        config: Application configuration (DI)

    Returns:
        Detailed information about service readiness
    """
    if config is None:
        config = Depends(ConfigDep)

    logger.debug("Readiness check requested")

    # Create health checker
    checker = ServiceHealthChecker(config)

    # Check all services in parallel
    services_status = await checker.check_all_services()

    # Determine overall status
    all_healthy = all(
        service["status"] == "healthy" for service in services_status.values()
    )

    if all_healthy:
        overall_status = "ready"
        status_code = status.HTTP_200_OK
        logger.info("Readiness check passed - all services are healthy")
    else:
        overall_status = "not_ready"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        unhealthy_services = [
            name for name, svc in services_status.items() if svc["status"] != "healthy"
        ]
        logger.warning(
            "Readiness check failed - unhealthy services: %s",
            unhealthy_services,
        )

    response.status_code = status_code

    return {
        "status": overall_status,
        "service": "memology-ml-api",
        "version": "1.0.0",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "services": services_status,
    }


@router.get("/live", response_model=HealthResponse)
async def liveness_check(config: Depends | None = None) -> HealthResponse:
    """
    Liveness probe endpoint (Kubernetes-style).
    Returns OK if the application is alive and not deadlocked.
    Similar to basic health check but may include internal checks.

    Returns:
        Information about liveness status
    """
    if config is None:
        config = Depends(ConfigDep)

    logger.debug("Liveness check requested")

    return HealthResponse(
        status="alive",
        service="memology-ml-api",
        version="1.0.0",
        timestamp=datetime.now(tz=timezone.utc),
    )


@router.get("/services", response_model=dict)
async def services_status(config: Depends | None = None) -> dict[str, Any]:
    """
    Detailed status of all external services.
    Useful for monitoring and debugging.

    Args:
        config: Application configuration (DI)

    Returns:
        Detailed status of each service
    """
    if config is None:
        config = Depends(ConfigDep)

    logger.debug("Services status check requested")

    checker = ServiceHealthChecker(config)
    services_status = await checker.check_all_services()

    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "services": services_status,
    }
