"""Enrollment domain models and Pydantic schemas."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


@dataclass
class Enrollment:
    enrollment_id: int
    student_id: int
    course_id: int
    semester: int
    marks: Optional[Decimal] = None
    attendance_pct: Optional[Decimal] = None


class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    semester: int = Field(..., ge=1, le=12)
    marks: Optional[float] = Field(None, ge=0.0, le=100.0)
    attendance_pct: Optional[float] = Field(None, ge=0.0, le=100.0)


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentOut(EnrollmentBase):
    enrollment_id: int
    model_config = ConfigDict(from_attributes=True)


class EnrollmentDetailOut(BaseModel):
    enrollment_id: int
    course_id: int
    course_code: str
    course_name: str
    credits: int
    semester: int
    marks: Optional[float] = None
    attendance_pct: Optional[float] = None
    grade: Optional[str] = None
    is_passed: Optional[bool] = None
    is_at_risk: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)
