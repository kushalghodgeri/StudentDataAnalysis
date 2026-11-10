"""ReportPipeline Facade orchestrating ingestion, cleaning, multi-dimensional analysis, and reporting."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd

from app.analysis.attendance import AttendanceAnalyzer
from app.analysis.demographics import DemographicsAnalyzer
from app.analysis.performance import PerformanceAnalyzer
from app.config.settings import get_settings
from app.db.connection import DatabaseConnection, get_db
from app.db.repositories.course_repo import CourseRepository
from app.db.repositories.enrollment_repo import EnrollmentRepository
from app.db.repositories.student_repo import StudentRepository
from app.etl.importer import DataImporter
from app.reporting.charts import ChartBuilder
from app.reporting.summary_report import SummaryReport
from app.utils.exceptions import ResourceNotFoundError
from app.utils.logger import logger


class ReportPipeline:
    """Facade orchestrating the complete lifecycle: ingest -> clean -> analyze -> report."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db()
        self.student_repo = StudentRepository(self.db)
        self.course_repo = CourseRepository(self.db)
        self.enrollment_repo = EnrollmentRepository(self.db)
        self.importer = DataImporter(self.db)
        self.settings = get_settings()
        self.chart_builder = ChartBuilder(self.settings.charts_dir_path)
        self._reports_meta_file = self.settings.reports_dir_path / "reports_meta.json"

    def ingest_file(
        self, file_content: Union[bytes, Path, str], filename: str
    ) -> Tuple[int, Dict[str, int]]:
        """Ingest, stage, clean, and persist tabular dataset."""
        logger.info(f"Pipeline: Ingesting file '{filename}'")
        return self.importer.import_and_process(file_content, filename)

    def get_meta_filters(self) -> Dict[str, Any]:
        """Fetch distinct filter options (departments, semesters, courses)."""
        departments = self.student_repo.get_departments()
        semesters = self.enrollment_repo.get_semesters()
        courses = self.course_repo.list_all()
        return {
            "departments": departments,
            "semesters": semesters,
            "courses": courses,
        }

    def get_analytics_overview(
        self, semester: Optional[int] = None, department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve executive KPIs using SQL aggregations."""
        return self.enrollment_repo.get_overview_stats(semester, department)

    def get_performance_analytics(
        self, semester: Optional[int] = None, department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute performance metrics, letter grades, trends, and top/bottom rankings."""
        # 1. Fetch relevant dataset
        df = self.enrollment_repo.fetch_enrollment_df(semester, department)

        # 2. Run PerformanceAnalyzer
        analyzer = PerformanceAnalyzer(df)
        results = analyzer.analyze()

        # 3. If SQL view provides pre-aggregated dept averages / trends, cross-check or augment
        if not results["dept_averages"]:
            results["dept_averages"] = self.enrollment_repo.get_dept_averages(semester)
        if not results["semester_trend"]:
            results["semester_trend"] = self.enrollment_repo.get_semester_trends(department)

        return results

    def get_attendance_analytics(
        self, semester: Optional[int] = None, department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute attendance breakdowns, correlation, and at-risk students."""
        df = self.enrollment_repo.fetch_enrollment_df(semester, department)
        analyzer = AttendanceAnalyzer(df)
        results = analyzer.analyze()

        # Augment with SQL aggregations if df was empty or for fallback
        if not results["by_department"]:
            results["by_department"] = self.enrollment_repo.get_attendance_by_department(semester)
        if not results["at_risk"]:
            results["at_risk"] = self.enrollment_repo.get_at_risk_students(semester, department)

        return results

    def get_demographics_analytics(self) -> Dict[str, Any]:
        """Compute student demographic splits."""
        return self.student_repo.get_demographics()

    def generate_report(
        self,
        semester: Optional[int] = None,
        department: Optional[str] = None,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute end-to-end reporting pipeline and save charts and documents."""
        formats = formats or ["pdf", "csv", "xlsx"]
        report_id = f"rep_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{semester or 'all'}"
        logger.info(f"Pipeline: Generating report '{report_id}' for semester={semester}, dept={department}")

        # 1. Fetch analysis data
        df = self.enrollment_repo.fetch_enrollment_df(semester, department)
        overview_stats = self.get_analytics_overview(semester, department)
        perf_data = self.get_performance_analytics(semester, department)
        att_data = self.get_attendance_analytics(semester, department)

        # 2. Generate charts
        chart_paths = self.chart_builder.generate_all(df, prefix=report_id)
        charts_list = [
            {"name": p.name, "url": f"/api/v1/charts/{p.name}"}
            for p in chart_paths
        ]

        # 3. Generate summary reports (CSV, Excel, PDF)
        report_generator = SummaryReport(
            df=df,
            overview_stats=overview_stats,
            performance_data=perf_data,
            attendance_data=att_data,
            report_id=report_id,
            output_dir=self.settings.reports_dir_path,
            semester=semester,
            department=department,
        )
        file_paths = report_generator.generate(formats=formats)
        files_list = [
            {"name": p.name, "url": f"/api/v1/reports/{report_id}/download/{p.name}"}
            for fmt, p in file_paths.items()
        ]

        # 4. Save metadata for report listing
        self._record_report_meta(
            report_id=report_id,
            semester=semester,
            department=department,
            formats=formats,
            files=files_list,
            charts=charts_list,
        )

        return {
            "report_id": report_id,
            "files": files_list,
            "charts": charts_list,
        }

    def list_reports(self) -> List[Dict[str, Any]]:
        """List previously generated reports."""
        if not self._reports_meta_file.exists():
            return []
        try:
            with open(self._reports_meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read reports metadata file: {e}")
            return []

    def _record_report_meta(
        self,
        report_id: str,
        semester: Optional[int],
        department: Optional[str],
        formats: List[str],
        files: List[Dict[str, str]],
        charts: List[Dict[str, str]],
    ) -> None:
        """Persist report record to metadata file."""
        reports = self.list_reports()
        record = {
            "report_id": report_id,
            "created_at": datetime.now().isoformat(),
            "semester": semester,
            "department": department,
            "formats": formats,
            "files": files,
            "charts": charts,
        }
        reports.insert(0, record)
        try:
            with open(self._reports_meta_file, "w", encoding="utf-8") as f:
                json.dump(reports, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not write reports metadata: {e}")
