"""Student domain models and Pydantic schemas."""

from dataclasses import dataclass
from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enrollment import EnrollmentDetailOut


@dataclass
class Student:
    student_id: int
    first_name: str
    last_name: str
    email: str
    gender: str
    dob: date
    department: str
    admission_year: int


class StudentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., max_length=100)
    gender: Literal["M", "F", "O"]
    dob: date
    department: str = Field(..., min_length=1, max_length=80)
    admission_year: int = Field(..., ge=1990, le=2100)


class StudentCreate(StudentBase):
    pass


class StudentOut(StudentBase):
    student_id: int
    model_config = ConfigDict(from_attributes=True)


class StudentStats(BaseModel):
    total_enrolled_courses: int = 0
    gpa_marks_avg: Optional[float] = None
    overall_attendance_pct: Optional[float] = None
    total_courses_passed: int = 0


class StudentDetailOut(StudentOut):
    enrollments: List[EnrollmentDetailOut] = Field(default_factory=list)
    stats: StudentStats = Field(default_factory=StudentStats)
    model_config = ConfigDict(from_attributes=True)
