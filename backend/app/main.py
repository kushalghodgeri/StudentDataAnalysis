"""Main FastAPI application entrypoint with CORS, routing, and centralized error handling."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    analytics_router,
    health_router,
    imports_router,
    reports_router,
    students_router,
)
from app.config.settings import get_settings
from app.db.connection import DatabaseConnection
from app.utils.exceptions import BaseAppException
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    settings = get_settings()
    logger.info("Initializing Student Analytics API...")
    # Ensure directories exist
    settings.raw_dir_path
    settings.processed_dir_path
    settings.charts_dir_path
    settings.reports_dir_path

    yield

    logger.info("Shutting down Student Analytics API...")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    settings = get_settings()

    app = FastAPI(
        title="Student Data Analysis and Reporting Tool",
        description="High-performance backend API for student academic analytics, batch ETL, and PDF/Excel reports.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Centralized Custom Exception Handlers
    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(request: Request, exc: BaseAppException):
        logger.warning(f"Application error [{exc.code}] on {request.method} {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameter or payload structure.",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred.",
                }
            },
        )

    # Base path /api/v1 (REST API contract)
    api_v1 = APIRouter(prefix="/api/v1")
    api_v1.include_router(health_router)
    api_v1.include_router(imports_router)
    api_v1.include_router(students_router)
    api_v1.include_router(analytics_router)
    api_v1.include_router(reports_router)
    app.include_router(api_v1)

    # Direct top-level inclusion for convenience (e.g. GET /health)
    app.include_router(health_router)
    app.include_router(imports_router)
    app.include_router(students_router)
    app.include_router(analytics_router)
    app.include_router(reports_router)

    # Static charts mount
    charts_path = settings.charts_dir_path
    charts_path.mkdir(parents=True, exist_ok=True)
    app.mount("/charts", StaticFiles(directory=str(charts_path)), name="charts")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
