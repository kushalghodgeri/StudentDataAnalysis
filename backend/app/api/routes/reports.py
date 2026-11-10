"""Report generation and file download router."""

from pathlib import Path
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from app.config.settings import get_settings
from app.db.connection import DatabaseConnection, get_db
from app.models.report import ReportRequest, ReportResponse
from app.services.pipeline import ReportPipeline
from app.utils.exceptions import ResourceNotFoundError

router = APIRouter(tags=["Reports"])


@router.post("/reports/generate", response_model=ReportResponse)
def generate_report(
    payload: ReportRequest,
    db: DatabaseConnection = Depends(get_db),
):
    """Trigger report compilation pipeline across specified formats and charts."""
    pipeline = ReportPipeline(db)
    result = pipeline.generate_report(
        semester=payload.semester,
        department=payload.department,
        formats=payload.formats,
    )
    return result


@router.get("/reports", response_model=List[Dict[str, Any]])
def list_reports(db: DatabaseConnection = Depends(get_db)):
    """Retrieve catalog of generated analytical reports."""
    pipeline = ReportPipeline(db)
    return pipeline.list_reports()


@router.get("/reports/{report_id}/download/{filename}")
def download_report_file(
    report_id: str,
    filename: str,
):
    """Download generated PDF, CSV, or Excel report by filename."""
    settings = get_settings()
    file_path = settings.reports_dir_path / filename

    if not file_path.exists() or not file_path.is_file():
        raise ResourceNotFoundError("Report File", filename)

    media_type = "application/octet-stream"
    if filename.lower().endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.lower().endswith(".csv"):
        media_type = "text/csv"
    elif filename.lower().endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )


@router.get("/charts/{filename}")
def get_chart_image(filename: str):
    """Serve generated chart image as PNG."""
    settings = get_settings()
    file_path = settings.charts_dir_path / filename

    if not file_path.exists() or not file_path.is_file():
        raise ResourceNotFoundError("Chart Image", filename)

    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename=filename,
    )
