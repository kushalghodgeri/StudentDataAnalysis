"""Student router managing student querying, profile viewing, and filter metadata."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.db.connection import DatabaseConnection, get_db
from app.db.repositories.student_repo import StudentRepository
from app.models.analytics import MetaFiltersOut
from app.models.common import PaginatedResponse
from app.models.student import StudentDetailOut, StudentOut
from app.services.pipeline import ReportPipeline
from app.utils.exceptions import ResourceNotFoundError

router = APIRouter(tags=["Students"])


@router.get("/students", response_model=PaginatedResponse[StudentOut])
def list_students(
    page: int = Query(default=1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    department: Optional[str] = Query(default=None, description="Filter by department"),
    search: Optional[str] = Query(default=None, description="Search by name or email"),
    sort_by: str = Query(default="student_id", description="Sort column"),
    order: str = Query(default="ASC", pattern="^(?i)(ASC|DESC)$", description="Sort order"),
    db: DatabaseConnection = Depends(get_db),
):
    """Retrieve paginated student list with optional search and department filters."""
    repo = StudentRepository(db)
    items, total = repo.list_paginated(
        page=page,
        page_size=page_size,
        department=department,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/students/{id}", response_model=StudentDetailOut)
def get_student_details(
    id: int,
    db: DatabaseConnection = Depends(get_db),
):
    """Retrieve comprehensive profile, course enrollments, and aggregate KPIs for a student."""
    repo = StudentRepository(db)
    student = repo.get_student_detail(id)
    if not student:
        raise ResourceNotFoundError("Student", id)
    return student


@router.get("/meta/filters", response_model=MetaFiltersOut)
def get_meta_filters(db: DatabaseConnection = Depends(get_db)):
    """Fetch distinct departments, semesters, and courses for frontend dropdown filters."""
    pipeline = ReportPipeline(db)
    return pipeline.get_meta_filters()
