"""Import router handling CSV/Excel file uploads and historical logs."""

from typing import List
from fastapi import APIRouter, Depends, File, UploadFile
from app.db.connection import DatabaseConnection, get_db
from app.models.report import ImportLogOut, ImportResponse
from app.services.pipeline import ReportPipeline
from app.utils.exceptions import DataImportError
from app.utils.logger import logger

router = APIRouter(tags=["Imports"])


@router.post("/imports", response_model=ImportResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    db: DatabaseConnection = Depends(get_db),
):
    """Upload CSV or Excel dataset, load into staging, clean, and insert."""
    if not file.filename:
        raise DataImportError("No filename provided in upload.")

    filename = file.filename
    if not filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise DataImportError("Unsupported file extension. Only .csv and .xlsx are supported.")

    content = await file.read()
    if not content:
        raise DataImportError("Uploaded file is empty.")

    pipeline = ReportPipeline(db)
    import_id, summary = pipeline.ingest_file(content, filename)
    return {
        "import_id": import_id,
        "cleaning_summary": summary,
    }


@router.get("/imports", response_model=List[ImportLogOut])
def get_import_history(
    limit: int = 50,
    db: DatabaseConnection = Depends(get_db),
):
    """Retrieve historical dataset import executions."""
    pipeline = ReportPipeline(db)
    return pipeline.importer.list_import_logs(limit=limit)
