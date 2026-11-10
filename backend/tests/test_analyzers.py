"""Unit tests for Performance, Attendance, and Demographics analyzers."""

import numpy as np
import pandas as pd
import pytest
from app.analysis.attendance import AttendanceAnalyzer
from app.analysis.demographics import DemographicsAnalyzer
from app.analysis.performance import PerformanceAnalyzer


def test_performance_analyzer(sample_clean_df):
    analyzer = PerformanceAnalyzer(sample_clean_df)
    results = analyzer.analyze()

    assert "stats" in results
    stats = results["stats"]
    assert stats["count"] == 6
    assert stats["mean"] == pytest.approx(66.83, 0.1)
    assert stats["min"] == 35.0
    assert stats["max"] == 94.0
    assert "percentiles" in stats
    assert stats["percentiles"]["p50"] is not None
    assert stats["pass_rate"] == pytest.approx(83.33, 0.1)

    # Grade distribution
    grades = results["grade_distribution"]
    assert "A" in grades
    assert "B" in grades
    assert "C" in grades
    assert "D" in grades
    assert "F" in grades
    assert grades["A"] == 2  # 88, 94
    assert grades["F"] == 1  # 35

    # Department averages
    dept_avgs = results["dept_averages"]
    assert "Computer Science" in dept_avgs
    assert dept_avgs["Computer Science"] == pytest.approx(86.0, 0.1)

    # Top 10 and Bottom 10
    assert len(results["top10"]) > 0
    assert len(results["bottom10"]) > 0
    assert results["top10"][0]["marks_avg"] >= results["bottom10"][0]["marks_avg"]


def test_performance_analyzer_empty():
    analyzer = PerformanceAnalyzer(pd.DataFrame())
    results = analyzer.analyze()
    assert results["stats"]["count"] == 0
    assert results["stats"]["mean"] is None
    assert results["top10"] == []


def test_attendance_analyzer(sample_clean_df):
    analyzer = AttendanceAnalyzer(sample_clean_df)
    results = analyzer.analyze()

    # Department attendance
    by_dept = results["by_department"]
    assert "Computer Science" in by_dept
    assert by_dept["Computer Science"] > 80.0

    # Pearson correlation
    corr = results["correlation"]
    assert corr is not None
    assert -1.0 <= corr <= 1.0

    # At-risk students (marks < 40 and attendance < 75)
    at_risk = results["at_risk"]
    assert len(at_risk) == 1
    assert at_risk[0]["student_id"] == 102  # Bob Jones (marks 35, att 60)
    assert at_risk[0]["full_name"] == "Bob Jones"


def test_attendance_analyzer_empty():
    analyzer = AttendanceAnalyzer(pd.DataFrame())
    results = analyzer.analyze()
    assert results["by_department"] == {}
    assert results["correlation"] is None
    assert results["at_risk"] == []


def test_demographics_analyzer(sample_clean_df):
    analyzer = DemographicsAnalyzer(sample_clean_df)
    results = analyzer.analyze()

    # Gender breakdown (5 distinct students: Alice, Bob, Charlie, Diana, Evan)
    gender = results["gender"]
    assert gender.get("F", 0) == 2  # Alice, Diana
    assert gender.get("M", 0) == 2  # Bob, Evan
    assert gender.get("O", 0) == 1  # Charlie

    # Department counts
    dept_counts = results["department_counts"]
    assert dept_counts.get("Computer Science", 0) == 2

    # Cohorts
    cohorts = results["cohorts"]
    assert "2022" in cohorts


def test_demographics_analyzer_empty():
    analyzer = DemographicsAnalyzer(pd.DataFrame())
    results = analyzer.analyze()
    assert results["gender"] == {}
    assert results["department_counts"] == {}
    assert results["cohorts"] == {}
