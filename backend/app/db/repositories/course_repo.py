"""Course repository for database interactions."""

from typing import Any, Dict, List, Optional, Tuple
from app.db.repositories.base_repo import BaseRepository


class CourseRepository(BaseRepository):
    """Repository managing courses table."""

    def get_by_id(self, course_id: int) -> Optional[Dict[str, Any]]:
        """Fetch course by primary key."""
        query = """
            SELECT course_id, course_code, course_name, credits
            FROM courses
            WHERE course_id = %s;
        """
        return self.fetch_one(query, (course_id,))

    def get_by_code(self, course_code: str) -> Optional[Dict[str, Any]]:
        """Fetch course by unique course code."""
        query = """
            SELECT course_id, course_code, course_name, credits
            FROM courses
            WHERE course_code = %s;
        """
        return self.fetch_one(query, (course_code.upper().strip(),))

    def list_all(self) -> List[Dict[str, Any]]:
        """Fetch all courses ordered by code."""
        query = """
            SELECT course_id, course_code, course_name, credits
            FROM courses
            ORDER BY course_code ASC;
        """
        return self.fetch_all(query)

    def create_or_get(self, course_code: str, course_name: str, credits: int = 3) -> int:
        """Insert course if not exists, returning course_id."""
        existing = self.get_by_code(course_code)
        if existing:
            return existing["course_id"]

        query = """
            INSERT INTO courses (course_code, course_name, credits)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE course_name = VALUES(course_name), credits = VALUES(credits);
        """
        self.execute(query, (course_code.upper().strip(), course_name.strip(), credits))
        record = self.get_by_code(course_code)
        return record["course_id"] if record else 0

    def bulk_insert(self, courses: List[Tuple[Any, ...]]) -> int:
        """Bulk insert courses with ON DUPLICATE KEY UPDATE."""
        if not courses:
            return 0
        query = """
            INSERT INTO courses (course_code, course_name, credits)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                course_name = VALUES(course_name),
                credits = VALUES(credits);
        """
        return self.execute_many(query, courses)
