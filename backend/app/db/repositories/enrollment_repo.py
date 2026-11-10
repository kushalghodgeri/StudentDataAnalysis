"""Enrollment repository providing optimized aggregation queries and DataFrame extraction."""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from app.db.repositories.base_repo import BaseRepository


class EnrollmentRepository(BaseRepository):
    """Repository managing enrollments and views for reporting/analytics."""

    def bulk_insert(self, enrollments: List[Tuple[Any, ...]]) -> int:
        """Bulk insert enrollments with executemany."""
        if not enrollments:
            return 0
        query = """
            INSERT INTO enrollments (student_id, course_id, semester, marks, attendance_pct)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                marks = VALUES(marks),
                attendance_pct = VALUES(attendance_pct);
        """
        return self.execute_many(query, enrollments)

    def get_semesters(self) -> List[int]:
        """Fetch distinct semester numbers present in enrollment data."""
        query = """
            SELECT DISTINCT semester
            FROM enrollments
            ORDER BY semester ASC;
        """
        rows = self.fetch_all(query)
        return [int(r["semester"]) for r in rows]

    def fetch_enrollment_df(
        self, semester: Optional[int] = None, department: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch joined enrollment details into a DataFrame with selective columns."""
        where_clauses = []
        params: List[Any] = []

        if semester is not None:
            where_clauses.append("semester = %s")
            params.append(semester)

        if department:
            where_clauses.append("department = %s")
            params.append(department)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        query = f"""
            SELECT 
                enrollment_id,
                student_id,
                full_name,
                email,
                gender,
                department,
                admission_year,
                course_id,
                course_code,
                course_name,
                credits,
                semester,
                marks,
                attendance_pct,
                grade,
                is_passed,
                is_at_risk
            FROM vw_enrollment_detail
            {where_sql};
        """
        return self.fetch_df(query, tuple(params))

    def get_overview_stats(
        self, semester: Optional[int] = None, department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compute system overview KPIs entirely in SQL for maximum efficiency."""
        where_clauses = []
        params: List[Any] = []

        if semester is not None:
            where_clauses.append("semester = %s")
            params.append(semester)

        if department:
            where_clauses.append("department = %s")
            params.append(department)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        query = f"""
            SELECT 
                COUNT(DISTINCT student_id) AS total_students,
                COUNT(DISTINCT course_id) AS total_courses,
                ROUND(AVG(marks), 2) AS avg_marks,
                ROUND(AVG(attendance_pct), 2) AS avg_attendance,
                ROUND((SUM(CASE WHEN marks >= 40.0 THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(enrollment_id), 0), 2) AS pass_rate,
                SUM(CASE WHEN attendance_pct < 75.0 AND marks < 40.0 THEN 1 ELSE 0 END) AS at_risk_count
            FROM vw_enrollment_detail
            {where_sql};
        """
        row = self.fetch_one(query, tuple(params))
        if not row:
            return {
                "total_students": 0,
                "total_courses": 0,
                "avg_marks": None,
                "avg_attendance": None,
                "pass_rate": None,
                "at_risk_count": 0,
            }

        return {
            "total_students": int(row["total_students"] or 0),
            "total_courses": int(row["total_courses"] or 0),
            "avg_marks": float(row["avg_marks"]) if row["avg_marks"] is not None else None,
            "avg_attendance": float(row["avg_attendance"]) if row["avg_attendance"] is not None else None,
            "pass_rate": float(row["pass_rate"]) if row["pass_rate"] is not None else None,
            "at_risk_count": int(row["at_risk_count"] or 0),
        }

    def get_dept_averages(self, semester: Optional[int] = None) -> Dict[str, float]:
        """Compute average marks grouped by department via SQL GROUP BY."""
        where_sql = "WHERE semester = %s" if semester is not None else ""
        params = (semester,) if semester is not None else ()

        query = f"""
            SELECT department, ROUND(AVG(marks), 2) AS dept_avg
            FROM vw_enrollment_detail
            {where_sql}
            GROUP BY department
            ORDER BY dept_avg DESC;
        """
        rows = self.fetch_all(query, params)
        return {r["department"]: float(r["dept_avg"]) for r in rows if r["dept_avg"] is not None}

    def get_semester_trends(self, department: Optional[str] = None) -> Dict[str, float]:
        """Compute average marks trend across semesters via SQL GROUP BY."""
        where_sql = "WHERE department = %s" if department else ""
        params = (department,) if department else ()

        query = f"""
            SELECT semester, ROUND(AVG(marks), 2) AS sem_avg
            FROM vw_enrollment_detail
            {where_sql}
            GROUP BY semester
            ORDER BY semester ASC;
        """
        rows = self.fetch_all(query, params)
        return {f"Sem {r['semester']}": float(r["sem_avg"]) for r in rows if r["sem_avg"] is not None}

    def get_grade_distribution(
        self, semester: Optional[int] = None, department: Optional[str] = None
    ) -> Dict[str, int]:
        """Calculate letter grade distribution (A, B, C, D, F) in SQL."""
        where_clauses = []
        params: List[Any] = []

        if semester is not None:
            where_clauses.append("semester = %s")
            params.append(semester)

        if department:
            where_clauses.append("department = %s")
            params.append(department)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        query = f"""
            SELECT grade, COUNT(enrollment_id) AS cnt
            FROM vw_enrollment_detail
            {where_sql}
            GROUP BY grade
            ORDER BY grade ASC;
        """
        rows = self.fetch_all(query, tuple(params))
        dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for r in rows:
            g = r["grade"]
            if g in dist:
                dist[g] = int(r["cnt"])
        return dist

    def get_top_and_bottom_students(
        self, semester: Optional[int] = None, department: Optional[str] = None, limit: int = 10
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Retrieve top 10 and bottom 10 performing students based on average marks."""
        where_clauses = []
        params: List[Any] = []

        if semester is not None:
            where_clauses.append("semester = %s")
            params.append(semester)

        if department:
            where_clauses.append("department = %s")
            params.append(department)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        base_query = f"""
            SELECT 
                student_id,
                full_name,
                department,
                ROUND(AVG(marks), 2) AS marks_avg,
                COUNT(enrollment_id) AS enrolled_courses
            FROM vw_enrollment_detail
            {where_sql}
            GROUP BY student_id, full_name, department
            HAVING marks_avg IS NOT NULL
        """

        top_query = f"{base_query} ORDER BY marks_avg DESC LIMIT %s;"
        bottom_query = f"{base_query} ORDER BY marks_avg ASC LIMIT %s;"

        top_rows = self.fetch_all(top_query, tuple(params + [limit]))
        bottom_rows = self.fetch_all(bottom_query, tuple(params + [limit]))

        def format_rows(rows):
            return [
                {
                    "student_id": int(r["student_id"]),
                    "full_name": r["full_name"],
                    "department": r["department"],
                    "marks_avg": float(r["marks_avg"]),
                    "enrolled_courses": int(r["enrolled_courses"]),
                }
                for r in rows
            ]

        return format_rows(top_rows), format_rows(bottom_rows)

    def get_attendance_by_department(self, semester: Optional[int] = None) -> Dict[str, float]:
        """Average attendance percentage by department."""
        where_sql = "WHERE semester = %s" if semester is not None else ""
        params = (semester,) if semester is not None else ()

        query = f"""
            SELECT department, ROUND(AVG(attendance_pct), 2) AS avg_att
            FROM vw_enrollment_detail
            {where_sql}
            GROUP BY department
            ORDER BY avg_att DESC;
        """
        rows = self.fetch_all(query, params)
        return {r["department"]: float(r["avg_att"]) for r in rows if r["avg_att"] is not None}

    def get_at_risk_students(
        self, semester: Optional[int] = None, department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Identify students with attendance < 75% and marks < 40."""
        where_clauses = ["attendance_pct < 75.0", "marks < 40.0"]
        params: List[Any] = []

        if semester is not None:
            where_clauses.append("semester = %s")
            params.append(semester)

        if department:
            where_clauses.append("department = %s")
            params.append(department)

        where_sql = f"WHERE {' AND '.join(where_clauses)}"

        query = f"""
            SELECT 
                student_id,
                full_name,
                department,
                semester,
                course_code,
                marks,
                attendance_pct
            FROM vw_enrollment_detail
            {where_sql}
            ORDER BY marks ASC, attendance_pct ASC;
        """
        rows = self.fetch_all(query, tuple(params))
        return [
            {
                "student_id": int(r["student_id"]),
                "full_name": r["full_name"],
                "department": r["department"],
                "semester": int(r["semester"]),
                "course_code": r["course_code"],
                "marks": float(r["marks"]) if r["marks"] is not None else 0.0,
                "attendance_pct": float(r["attendance_pct"]) if r["attendance_pct"] is not None else 0.0,
            }
            for r in rows
        ]
