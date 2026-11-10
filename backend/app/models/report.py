"""Reporting, Import and Pipeline Pydantic schemas."""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class CleaningSummary(BaseModel):
    rows_in: int = 0
    rows_out: int = 0
    duplicates_removed: int = 0
    nulls_filled: int = 0
    outliers_flagged: int = 0


class ImportResponse(BaseModel):
    import_id: int
    cleaning_summary: CleaningSummary


class ImportLogOut(BaseModel):
    import_id: int
    file_name: str
    file_type: str
    total_rows: int
    valid_rows: int
    rejected_rows: int
    duplicates_removed: int
    nulls_filled: int
    outliers_flagged: int
    status: str
    error_summary: Optional[str] = None
    imported_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ReportRequest(BaseModel):
    semester: Optional[int] = Field(None, ge=1, le=12, description="Target semester filter")
    department: Optional[str] = Field(None, max_length=80, description="Optional department filter")
    formats: List[Literal["pdf", "csv", "xlsx"]] = Field(
        default=["pdf", "csv", "xlsx"],
        description="Target export formats"
    )


class ReportFileItem(BaseModel):
    name: str
    url: str


class ReportResponse(BaseModel):
    report_id: str
    files: List[ReportFileItem]
    charts: List[ReportFileItem]


class ReportMetadata(BaseModel):
    report_id: str
    created_at: datetime
    semester: Optional[int] = None
    department: Optional[str] = None
    formats: List[str]
    files: List[str]
    charts: List[str]
