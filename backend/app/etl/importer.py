"""DataImporter: Reads CSV/Excel, loads staging table, cleans, and bulk inserts to relational tables."""

import io
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
from app.db.connection import DatabaseConnection, get_db
from app.db.repositories.course_repo import CourseRepository
from app.db.repositories.enrollment_repo import EnrollmentRepository
from app.db.repositories.student_repo import StudentRepository
from app.etl.cleaner import DataCleaner
from app.utils.exceptions import DataImportError
from app.utils.logger import logger


class DataImporter:
    """Importer pipeline managing file parsing, staging storage, cleaning, and bulk persistence."""

    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db()
        self.student_repo = StudentRepository(self.db)
        self.course_repo = CourseRepository(self.db)
        self.enrollment_repo = EnrollmentRepository(self.db)

    def parse_file(
        self, file_content: Union[bytes, Path, str], filename: str
    ) -> pd.DataFrame:
        """Parse raw CSV or Excel payload into a Pandas DataFrame."""
        try:
            if filename.lower().endswith(".csv"):
                if isinstance(file_content, bytes):
                    return pd.read_csv(io.BytesIO(file_content))
                return pd.read_csv(file_content)
            elif filename.lower().endswith((".xlsx", ".xls")):
                if isinstance(file_content, bytes):
                    return pd.read_excel(io.BytesIO(file_content), engine="openpyxl")
                return pd.read_excel(file_content, engine="openpyxl")
            else:
                raise DataImportError(
                    f"Unsupported file format '{filename}'. Please upload .csv or .xlsx files."
                )
        except Exception as e:
            logger.error(f"Failed to parse import file {filename}: {e}")
            raise DataImportError(f"Could not parse uploaded file: {str(e)}") from e

    def stage_raw_data(self, df: pd.DataFrame, batch_id: str) -> int:
        """Store raw unprocessed rows into stg_student_raw for data auditing."""
        staging_cols = [
            "batch_id", "student_id", "first_name", "last_name", "email", "gender",
            "dob", "department", "admission_year", "course_code", "course_name",
            "credits", "semester", "marks", "attendance_pct"
        ]
        
        # Prepare parameters list
        rows_to_insert = []
        for _, row in df.iterrows():
            record = (
                batch_id,
                str(row.get("student_id", ""))[:50] if pd.notna(row.get("student_id")) else None,
                str(row.get("first_name", ""))[:100] if pd.notna(row.get("first_name")) else None,
                str(row.get("last_name", ""))[:100] if pd.notna(row.get("last_name")) else None,
                str(row.get("email", ""))[:150] if pd.notna(row.get("email")) else None,
                str(row.get("gender", ""))[:20] if pd.notna(row.get("gender")) else None,
                str(row.get("dob", ""))[:50] if pd.notna(row.get("dob")) else None,
                str(row.get("department", ""))[:100] if pd.notna(row.get("department")) else None,
                str(row.get("admission_year", ""))[:20] if pd.notna(row.get("admission_year")) else None,
                str(row.get("course_code", ""))[:50] if pd.notna(row.get("course_code")) else None,
                str(row.get("course_name", ""))[:150] if pd.notna(row.get("course_name")) else None,
                str(row.get("credits", ""))[:20] if pd.notna(row.get("credits")) else None,
                str(row.get("semester", ""))[:20] if pd.notna(row.get("semester")) else None,
                str(row.get("marks", ""))[:30] if pd.notna(row.get("marks")) else None,
                str(row.get("attendance_pct", ""))[:30] if pd.notna(row.get("attendance_pct")) else None,
            )
            rows_to_insert.append(record)

        query = f"""
            INSERT INTO stg_student_raw (
                {", ".join(staging_cols)}, import_status
            ) VALUES (
                {", ".join(["%s"] * len(staging_cols))}, 'PENDING'
            );
        """
        try:
            return self.student_repo.execute_many(query, rows_to_insert)
        except Exception as e:
            logger.warning(f"Could not stage raw data: {e}")
            return 0

    def import_and_process(
        self, file_content: Union[bytes, Path, str], filename: str
    ) -> Tuple[int, Dict[str, int]]:
        """Complete ingestion pipeline: parse -> stage -> clean -> bulk insert -> log."""
        batch_id = str(uuid.uuid4())
        logger.info(f"Starting import for file '{filename}' with batch_id: {batch_id}")

        raw_df = self.parse_file(file_content, filename)
        total_rows = len(raw_df)

        # 1. Insert into Staging Table
        self.stage_raw_data(raw_df, batch_id)

        # 2. Run Data Cleaner
        cleaner = DataCleaner(raw_df).clean_all()
        cleaned_df = cleaner.df
        summary = cleaner.get_summary()

        # 3. Persist Validated Data via executemany
        valid_rows = len(cleaned_df)
        rejected_rows = total_rows - valid_rows
        status = "SUCCESS" if rejected_rows == 0 else ("PARTIAL" if valid_rows > 0 else "FAILED")

        try:
            self._persist_cleaned_data(cleaned_df)
        except Exception as e:
            logger.error(f"Error persisting cleaned data: {e}")
            self._log_import(
                filename, total_rows, 0, total_rows, summary, "FAILED", str(e)
            )
            raise DataImportError(f"Failed to persist imported data: {str(e)}") from e

        # 4. Record to import_logs
        import_id = self._log_import(
            filename, total_rows, valid_rows, rejected_rows, summary, status
        )

        logger.info(
            f"Import #{import_id} complete: {valid_rows}/{total_rows} rows inserted, "
            f"duplicates={summary['duplicates_removed']}, nulls_filled={summary['nulls_filled']}, "
            f"outliers={summary['outliers_flagged']}"
        )
        return import_id, summary

    def _persist_cleaned_data(self, df: pd.DataFrame) -> None:
        """Batch insert cleaned records into students, courses, and enrollments."""
        if df.empty:
            return

        # 1. Bulk Upsert Students
        if all(c in df.columns for c in ["first_name", "last_name", "email"]):
            student_cols = ["first_name", "last_name", "email", "gender", "dob", "department", "admission_year"]
            available_cols = [c for c in student_cols if c in df.columns]
            
            # Group by email to ensure unique student rows for insertion
            student_df = df.drop_duplicates(subset=["email"]).copy()
            students_data = []
            for _, r in student_df.iterrows():
                students_data.append((
                    str(r.get("first_name", "")),
                    str(r.get("last_name", "")),
                    str(r.get("email", "")),
                    str(r.get("gender", "O")),
                    r.get("dob"),
                    str(r.get("department", "General")),
                    int(r.get("admission_year", 2022)),
                ))
            self.student_repo.bulk_insert(students_data)

        # 2. Bulk Upsert Courses
        if "course_code" in df.columns:
            course_df = df.drop_duplicates(subset=["course_code"]).copy()
            courses_data = []
            for _, r in course_df.iterrows():
                code = str(r.get("course_code", "")).strip().upper()
                name = str(r.get("course_name", code))
                credits = int(r.get("credits", 3))
                if code:
                    courses_data.append((code, name, credits))
            self.course_repo.bulk_insert(courses_data)

        # 3. Bulk Insert Enrollments
        if all(c in df.columns for c in ["email", "course_code", "semester"]):
            # Build student email -> student_id mapping
            email_list = df["email"].unique().tolist()
            students_in_db = self.student_repo.fetch_all(
                "SELECT student_id, email FROM students WHERE email IN (%s)" %
                ",".join(["%s"] * len(email_list)),
                tuple(email_list)
            ) if email_list else []
            email_to_id = {s["email"].lower(): s["student_id"] for s in students_in_db}

            # Build course_code -> course_id mapping
            code_list = df["course_code"].str.upper().unique().tolist()
            courses_in_db = self.course_repo.fetch_all(
                "SELECT course_id, course_code FROM courses WHERE course_code IN (%s)" %
                ",".join(["%s"] * len(code_list)),
                tuple(code_list)
            ) if code_list else []
            code_to_id = {c["course_code"].upper(): c["course_id"] for c in courses_in_db}

            enrollments_data = []
            for _, r in df.iterrows():
                s_id = email_to_id.get(str(r.get("email", "")).lower())
                c_id = code_to_id.get(str(r.get("course_code", "")).upper())
                sem = int(r.get("semester", 1))
                marks = float(r["marks"]) if pd.notna(r.get("marks")) else None
                att = float(r["attendance_pct"]) if pd.notna(r.get("attendance_pct")) else None
                if s_id and c_id:
                    enrollments_data.append((s_id, c_id, sem, marks, att))

            if enrollments_data:
                self.enrollment_repo.bulk_insert(enrollments_data)

    def _log_import(
        self,
        filename: str,
        total: int,
        valid: int,
        rejected: int,
        summary: Dict[str, int],
        status: str,
        error_summary: Optional[str] = None,
    ) -> int:
        """Create an entry in import_logs table."""
        file_type = "CSV" if filename.lower().endswith(".csv") else "EXCEL"
        query = """
            INSERT INTO import_logs (
                file_name, file_type, total_rows, valid_rows, rejected_rows,
                duplicates_removed, nulls_filled, outliers_flagged, status, error_summary
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            filename,
            file_type,
            total,
            valid,
            rejected,
            summary.get("duplicates_removed", 0),
            summary.get("nulls_filled", 0),
            summary.get("outliers_flagged", 0),
            status,
            error_summary,
        )
        try:
            return self.student_repo.execute(query, params)
        except Exception as e:
            logger.warning(f"Could not write import log: {e}")
            return 0

    def list_import_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List historical import logs."""
        query = """
            SELECT 
                import_id, file_name, file_type, total_rows, valid_rows, rejected_rows,
                duplicates_removed, nulls_filled, outliers_flagged, status, error_summary,
                imported_at
            FROM import_logs
            ORDER BY import_id DESC
            LIMIT %s;
        """
        return self.student_repo.fetch_all(query, (limit,))
