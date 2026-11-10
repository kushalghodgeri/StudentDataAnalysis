"""Student repository for queries, pagination, search, and bulk operations."""

from typing import Any, Dict, List, Optional, Tuple
from app.db.repositories.base_repo import BaseRepository
from app.utils.logger import logger


class StudentRepository(BaseRepository):
    """Repository managing students table and related views."""

    ALLOWED_SORT_COLUMNS = {
        "student_id": "student_id",
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email",
        "department": "department",
        "admission_year": "admission_year",
    }

    def get_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Fetch student record by primary key."""
        query = """
            SELECT student_id, first_name, last_name, email, gender, dob, department, admission_year
            FROM students
            WHERE student_id = %s;
        """
        return self.fetch_one(query, (student_id,))

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch student record by unique email."""
        query = """
            SELECT student_id, first_name, last_name, email, gender, dob, department, admission_year
            FROM students
            WHERE email = %s;
        """
        return self.fetch_one(query, (email.lower(),))

    def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        department: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "student_id",
        order: str = "ASC",
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Fetch paginated, filtered, and sorted students using parameterized queries."""
        sort_col = self.ALLOWED_SORT_COLUMNS.get(sort_by, "student_id")
        sort_dir = "DESC" if order.upper() == "DESC" else "ASC"

        where_clauses = []
        params: List[Any] = []

        if department:
            where_clauses.append("department = %s")
            params.append(department)

        if search:
            search_param = f"%{search.strip()}%"
            where_clauses.append(
                "(first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)"
            )
            params.extend([search_param, search_param, search_param])

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Count total matches
        count_sql = f"""
            SELECT COUNT(student_id) AS total_count
            FROM students
            {where_sql};
        """
        count_res = self.fetch_one(count_sql, tuple(params))
        total = count_res["total_count"] if count_res else 0

        # Paginated items
        offset = (page - 1) * page_size
        items_sql = f"""
            SELECT student_id, first_name, last_name, email, gender, dob, department, admission_year
            FROM students
            {where_sql}
            ORDER BY {sort_col} {sort_dir}
            LIMIT %s OFFSET %s;
        """
        items_params = tuple(params + [page_size, offset])
        items = self.fetch_all(items_sql, items_params)
        return items, total

    def get_student_detail(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Fetch full student profile including enrollments and summary statistics."""
        student = self.get_by_id(student_id)
        if not student:
            return None

        # Fetch aggregated stats from summary view
        summary_sql = """
            SELECT 
                total_enrolled_courses,
                gpa_marks_avg,
                overall_attendance_pct,
                total_courses_passed
            FROM vw_student_summary
            WHERE student_id = %s;
        """
        stats_row = self.fetch_one(summary_sql, (student_id,))
        stats = {
            "total_enrolled_courses": int(stats_row["total_enrolled_courses"]) if stats_row and stats_row["total_enrolled_courses"] else 0,
            "gpa_marks_avg": float(stats_row["gpa_marks_avg"]) if stats_row and stats_row["gpa_marks_avg"] is not None else None,
            "overall_attendance_pct": float(stats_row["overall_attendance_pct"]) if stats_row and stats_row["overall_attendance_pct"] is not None else None,
            "total_courses_passed": int(stats_row["total_courses_passed"]) if stats_row and stats_row["total_courses_passed"] else 0,
        }

        # Fetch course enrollments
        enrollment_sql = """
            SELECT 
                enrollment_id,
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
            WHERE student_id = %s
            ORDER BY semester ASC, course_code ASC;
        """
        enrollments = self.fetch_all(enrollment_sql, (student_id,))
        # Convert numeric types
        for e in enrollments:
            e["marks"] = float(e["marks"]) if e["marks"] is not None else None
            e["attendance_pct"] = float(e["attendance_pct"]) if e["attendance_pct"] is not None else None
            e["is_passed"] = bool(e["is_passed"])
            e["is_at_risk"] = bool(e["is_at_risk"])

        result = dict(student)
        result["stats"] = stats
        result["enrollments"] = enrollments
        return result

    def bulk_insert(self, students: List[Tuple[Any, ...]]) -> int:
        """Bulk insert students using executemany with duplicate handling."""
        if not students:
            return 0
        query = """
            INSERT INTO students (first_name, last_name, email, gender, dob, department, admission_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                first_name = VALUES(first_name),
                last_name = VALUES(last_name),
                department = VALUES(department),
                dob = VALUES(dob),
                gender = VALUES(gender),
                admission_year = VALUES(admission_year);
        """
        return self.execute_many(query, students)

    def get_departments(self) -> List[str]:
        """Fetch distinct departments for filter dropdowns."""
        query = """
            SELECT DISTINCT department
            FROM students
            WHERE department IS NOT NULL AND department != ''
            ORDER BY department ASC;
        """
        rows = self.fetch_all(query)
        return [r["department"] for r in rows]

    def get_demographics(self) -> Dict[str, Any]:
        """Compute demographic distributions directly via SQL aggregation."""
        gender_query = """
            SELECT gender, COUNT(student_id) AS cnt
            FROM students
            GROUP BY gender;
        """
        gender_rows = self.fetch_all(gender_query)
        gender_dict = {
            r["gender"]: int(r.get("cnt", 1))
            for r in gender_rows
            if "gender" in r and r.get("gender")
        }

        dept_query = """
            SELECT department, COUNT(student_id) AS cnt
            FROM students
            GROUP BY department
            ORDER BY cnt DESC;
        """
        dept_rows = self.fetch_all(dept_query)
        dept_dict = {
            r["department"]: int(r.get("cnt", 1))
            for r in dept_rows
            if "department" in r and r.get("department")
        }

        cohort_query = """
            SELECT admission_year, COUNT(student_id) AS cnt
            FROM students
            GROUP BY admission_year
            ORDER BY admission_year ASC;
        """
        cohort_rows = self.fetch_all(cohort_query)
        cohort_dict = {
            str(r["admission_year"]): int(r.get("cnt", 1))
            for r in cohort_rows
            if "admission_year" in r and r.get("admission_year")
        }

        return {
            "gender": gender_dict,
            "department_counts": dept_dict,
            "cohorts": cohort_dict,
        }
