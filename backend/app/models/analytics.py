"""Analytics response models and data contracts."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OverviewAnalyticsOut(BaseModel):
    total_students: int
    total_courses: int
    avg_marks: Optional[float]
    pass_rate: Optional[float]
    avg_attendance: Optional[float]
    at_risk_count: int


class PercentilesOut(BaseModel):
    p25: Optional[float] = None
    p50: Optional[float] = None
    p75: Optional[float] = None
    p90: Optional[float] = None


class PerformanceStatsOut(BaseModel):
    count: int
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    percentiles: PercentilesOut = Field(default_factory=PercentilesOut)
    pass_rate: Optional[float] = None


class StudentRankingItem(BaseModel):
    student_id: int
    full_name: str
    department: str
    marks_avg: float
    enrolled_courses: int


class PerformanceAnalyticsOut(BaseModel):
    stats: PerformanceStatsOut
    grade_distribution: Dict[str, int]
    dept_averages: Dict[str, float]
    semester_trend: Dict[str, float]
    top10: List[StudentRankingItem]
    bottom10: List[StudentRankingItem]


class AtRiskStudentItem(BaseModel):
    student_id: int
    full_name: str
    department: str
    semester: int
    course_code: str
    marks: float
    attendance_pct: float


class AttendanceAnalyticsOut(BaseModel):
    by_department: Dict[str, float]
    correlation: Optional[float]
    at_risk: List[AtRiskStudentItem]


class DemographicsAnalyticsOut(BaseModel):
    gender: Dict[str, int]
    department_counts: Dict[str, int]
    cohorts: Dict[str, int]


class MetaFiltersOut(BaseModel):
    departments: List[str]
    semesters: List[int]
    courses: List[Dict[str, Any]]
