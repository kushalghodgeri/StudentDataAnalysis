"""Health check router reporting API and database connectivity status."""

from typing import Dict
from fastapi import APIRouter, Depends
from app.db.connection import DatabaseConnection, get_db

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=Dict[str, Any] if False else dict)
def health_check(db: DatabaseConnection = Depends(get_db)):
    """Check API service health and MySQL database connection."""
    db_connected = db.ping()
    status = "healthy" if db_connected else "degraded"
    return {
        "status": status,
        "db_connected": db_connected,
    }
