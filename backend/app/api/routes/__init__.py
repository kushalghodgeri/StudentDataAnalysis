from app.api.routes.health import router as health_router
from app.api.routes.imports import router as imports_router
from app.api.routes.students import router as students_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.reports import router as reports_router

__all__ = [
    "health_router",
    "imports_router",
    "students_router",
    "analytics_router",
    "reports_router",
]
