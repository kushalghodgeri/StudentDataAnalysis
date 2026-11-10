"""Course domain models and Pydantic schemas."""

from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


@dataclass
class Course:
    course_id: int
    course_code: str
    course_name: str
    credits: int


class CourseBase(BaseModel):
    course_code: str = Field(..., max_length=20)
    course_name: str = Field(..., max_length=150)
    credits: int = Field(default=3, ge=1, le=10)


class CourseCreate(CourseBase):
    pass


class CourseOut(CourseBase):
    course_id: int
    model_config = ConfigDict(from_attributes=True)
