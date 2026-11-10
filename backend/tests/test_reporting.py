"""Unit tests for ChartBuilder and SummaryReport modules."""

import os
from pathlib import Path
import pytest
from app.analysis.attendance import AttendanceAnalyzer
from app.analysis.performance import PerformanceAnalyzer
from app.reporting.charts import ChartBuilder
from app.reporting.summary_report import SummaryReport


def test_chart_builder_all_charts(sample_clean_df, tmp_path):
    builder = ChartBuilder(output_dir=tmp_path)
    charts = builder.generate_all(sample_clean_df, prefix="test")

    assert len(charts) == 7
    for c in charts:
        assert c.exists()
        assert c.stat().st_size > 0
        assert c.suffix == ".png"


def test_summary_report_generation(sample_clean_df, tmp_path):
    perf = PerformanceAnalyzer(sample_clean_df).analyze()
    att = AttendanceAnalyzer(sample_clean_df).analyze()
    overview = {
        "total_students": 5,
        "total_courses": 5,
        "avg_marks": 66.83,
        "avg_attendance": 81.83,
        "pass_rate": 83.33,
        "at_risk_count": 1,
    }

    report = SummaryReport(
        df=sample_clean_df,
        overview_stats=overview,
        performance_data=perf,
        attendance_data=att,
        report_id="unit_test_report",
        output_dir=tmp_path,
        semester=1,
        department="Computer Science",
    )

    files = report.generate(formats=["pdf", "csv", "xlsx"])

    assert "csv" in files
    assert "xlsx" in files
    assert "pdf" in files

    for fmt, p in files.items():
        assert p.exists()
        assert p.stat().st_size > 0
