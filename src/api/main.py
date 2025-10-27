"""
Главное FastAPI приложение.
Точка входа для API сервера.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from src.config.logging_config import LoggingConfigurator, get_logger
from src.api.routers import health, memes
from src.api.exceptions import MemeAPIException

# Инициализация логирования
LoggingConfigurator.configure()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager для FastAPI приложения.
    Выполняет инициализацию и cleanup.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Memology ML API")
    logger.info("=" * 60)

    # Здесь можно добавить инициализацию соединений, кэшей и т.д.
    # Например, проверку доступности Redis, Ollama, Stable Diffusion

    yield

    # Shutdown
    logger.info("Shutting down Memology ML API")


# Создание FastAPI приложения
app = FastAPI(
    title="Memology ML API",
    description="API для генерации мемов с использованием AI (Stable Diffusion + LLaMA)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование всех HTTP запросов."""
    start_time = time.time()

    logger.info(
        f"Incoming request: {request.method} {request.url.path} "
        f"from {request.client.host}"
    )

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"status={response.status_code} time={process_time:.3f}s"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(MemeAPIException)
async def meme_api_exception_handler(request: Request, exc: MemeAPIException):
    """Обработчик кастомных исключений API."""
    logger.error(
        f"API Exception: {exc.detail} (code: {exc.error_code}) at {request.url.path}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик неожиданных исключений."""
    logger.exception(f"Unhandled exception at {request.url.path}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Внутренняя ошибка сервера",
            "error_code": "INTERNAL_ERROR",
            "path": str(request.url.path),
        },
    )


# Подключение роутеров
app.include_router(health.router)
app.include_router(memes.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Корневой endpoint с информацией об API.
    """
    return {
        "service": "Memology ML API",
        "version": "1.0.0",
        "description": "AI-powered meme generation API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "generate_meme": "POST /api/memes/generate",
            "get_task_status": "GET /api/memes/task/{task_id}",
            "get_meme_result": "GET /api/memes/task/{task_id}/result",
            "available_styles": "GET /api/memes/styles",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,  # Используем нашу конфигурацию логирования
    )
