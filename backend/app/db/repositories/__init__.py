from app.db.repositories.base_repo import BaseRepository
from app.db.repositories.student_repo import StudentRepository
from app.db.repositories.course_repo import CourseRepository
from app.db.repositories.enrollment_repo import EnrollmentRepository

__all__ = [
    "BaseRepository",
    "StudentRepository",
    "CourseRepository",
    "EnrollmentRepository",
]
