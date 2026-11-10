"""Unit tests for DataCleaner class enforcing all business data quality rules."""

from datetime import date
import numpy as np
import pandas as pd
import pytest
from app.etl.cleaner import DataCleaner


def test_cleaner_drop_missing_identifiers(sample_dirty_df):
    cleaner = DataCleaner(sample_dirty_df)
    cleaner.drop_missing_identifiers()
    res_df = cleaner.df
    assert res_df["student_id"].isna().sum() == 0
    assert len(res_df) == len(sample_dirty_df) - 1


def test_cleaner_drop_duplicates(sample_dirty_df):
    cleaner = DataCleaner(sample_dirty_df)
    cleaner.drop_duplicates()
    assert cleaner.duplicates_removed >= 1


def test_cleaner_names_and_emails(sample_dirty_df):
    cleaner = DataCleaner(sample_dirty_df)
    cleaner.clean_names_and_emails()
    res_df = cleaner.df

    # Verify title casing and stripped whitespace
    alice_row = res_df[res_df["email"].str.contains("alice.wonder")]
    if not alice_row.empty:
        assert alice_row.iloc[0]["first_name"] == "Alice"
        assert alice_row.iloc[0]["last_name"] == "Wonder"
        assert alice_row.iloc[0]["email"] == "alice.wonder@example.com"

    # Verify invalid email was dropped
    assert "not_an_email_address" not in res_df["email"].values


def test_cleaner_cast_types_and_dates(sample_dirty_df):
    cleaner = DataCleaner(sample_dirty_df)
    cleaner.cast_types_and_parse_dates()
    res_df = cleaner.df

    assert pd.api.types.is_integer_dtype(res_df["admission_year"])
    assert pd.api.types.is_integer_dtype(res_df["semester"])
    # Check parsed date
    for d in res_df["dob"].dropna():
        assert isinstance(d, date)


def test_cleaner_scores_and_attendance_clipping():
    df = pd.DataFrame([
        {"student_id": 1, "marks": 105.0, "attendance_pct": -5.0},
        {"student_id": 2, "marks": -2.0, "attendance_pct": 102.0},
        {"student_id": 3, "marks": 75.0, "attendance_pct": 80.0},
    ])
    cleaner = DataCleaner(df)
    cleaner.clean_scores_and_attendance()
    res_df = cleaner.df

    assert (res_df["marks"] >= 0.0).all()
    assert (res_df["marks"] <= 100.0).all()
    assert (res_df["attendance_pct"] >= 0.0).all()
    assert (res_df["attendance_pct"] <= 100.0).all()
    assert res_df.loc[0, "marks"] == 100.0
    assert res_df.loc[0, "attendance_pct"] == 0.0


def test_cleaner_impute_missing_marks():
    df = pd.DataFrame([
        {"student_id": 1, "course_code": "CS101", "marks": 80.0, "attendance_pct": 90.0},
        {"student_id": 2, "course_code": "CS101", "marks": 90.0, "attendance_pct": 85.0},
        {"student_id": 3, "course_code": "CS101", "marks": np.nan, "attendance_pct": 80.0},  # should be 85.0
        {"student_id": 4, "course_code": "ME101", "marks": 60.0, "attendance_pct": np.nan},
    ])
    cleaner = DataCleaner(df)
    cleaner.impute_missing_marks()
    res_df = cleaner.df

    assert res_df["marks"].isna().sum() == 0
    # Median of 80 and 90 is 85.0
    assert res_df.loc[2, "marks"] == 85.0
    assert cleaner.nulls_filled >= 2


def test_cleaner_flag_outliers_iqr():
    # Construct dataset with clear outlier
    marks = [70.0, 72.0, 74.0, 75.0, 76.0, 78.0, 80.0, 5.0]  # 5.0 is an outlier
    df = pd.DataFrame({
        "student_id": list(range(1, 9)),
        "marks": marks,
    })
    cleaner = DataCleaner(df)
    cleaner.flag_outliers_iqr("marks")
    res_df = cleaner.df

    assert "is_outlier" in res_df.columns
    # Outliers should not be dropped, only flagged!
    assert len(res_df) == 8
    assert res_df.loc[res_df["marks"] == 5.0, "is_outlier"].iloc[0] == True
    assert cleaner.outliers_flagged == 1


def test_cleaner_clean_all_pipeline(sample_dirty_df):
    cleaner = DataCleaner(sample_dirty_df)
    cleaner.clean_all()
    summary = cleaner.get_summary()

    assert summary["rows_in"] == len(sample_dirty_df)
    assert summary["rows_out"] <= summary["rows_in"]
    assert summary["duplicates_removed"] >= 1
    assert summary["nulls_filled"] >= 1
    assert summary["outliers_flagged"] >= 1

    # Check chainability returns self
    c = DataCleaner(sample_dirty_df)
    assert c.drop_missing_identifiers().drop_duplicates() is c
