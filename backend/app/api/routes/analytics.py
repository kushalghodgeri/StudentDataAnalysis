"""Analytics router providing KPIs, academic performance, attendance, and demographics."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.db.connection import DatabaseConnection, get_db
from app.models.analytics import (
    AttendanceAnalyticsOut,
    DemographicsAnalyticsOut,
    OverviewAnalyticsOut,
    PerformanceAnalyticsOut,
)
from app.services.pipeline import ReportPipeline

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewAnalyticsOut)
def get_analytics_overview(
    semester: Optional[int] = Query(default=None, ge=1, le=12, description="Target semester"),
    department: Optional[str] = Query(default=None, description="Target department"),
    db: DatabaseConnection = Depends(get_db),
):
    """Retrieve overarching academic KPIs and at-risk totals."""
    pipeline = ReportPipeline(db)
    return pipeline.get_analytics_overview(semester, department)


@router.get("/performance", response_model=PerformanceAnalyticsOut)
def get_performance_analytics(
    semester: Optional[int] = Query(default=None, ge=1, le=12, description="Target semester"),
    department: Optional[str] = Query(default=None, description="Target department"),
    db: DatabaseConnection = Depends(get_db),
):
    """Retrieve performance statistics, letter grade distribution, trends, and rankings."""
    pipeline = ReportPipeline(db)
    return pipeline.get_performance_analytics(semester, department)


@router.get("/attendance", response_model=AttendanceAnalyticsOut)
def get_attendance_analytics(
    semester: Optional[int] = Query(default=None, ge=1, le=12, description="Target semester"),
    department: Optional[str] = Query(default=None, description="Target department"),
    db: DatabaseConnection = Depends(get_db),
):
    """Retrieve attendance metrics, Pearson correlation, and at-risk students."""
    pipeline = ReportPipeline(db)
    return pipeline.get_attendance_analytics(semester, department)


@router.get("/demographics", response_model=DemographicsAnalyticsOut)
def get_demographics_analytics(db: DatabaseConnection = Depends(get_db)):
    """Retrieve gender split, department headcounts, and admission cohorts."""
    pipeline = ReportPipeline(db)
    return pipeline.get_demographics_analytics()
