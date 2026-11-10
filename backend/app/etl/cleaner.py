"""Data cleaner implementing chainable cleaning rules and tracking metrics."""

from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from app.utils.validators import clean_name, is_valid_email, parse_date


class DataCleaner:
    """Chainable data cleaner enforcing data quality rules and collecting metrics."""

    def __init__(self, df: pd.DataFrame):
        self._df = df.copy()
        self.rows_in: int = len(self._df)
        self.duplicates_removed: int = 0
        self.nulls_filled: int = 0
        self.outliers_flagged: int = 0
        self.rows_out: int = self.rows_in

    @property
    def df(self) -> pd.DataFrame:
        """Access the underlying cleaned DataFrame."""
        return self._df

    def get_summary(self) -> Dict[str, int]:
        """Return a standardized cleaning summary report."""
        self.rows_out = len(self._df)
        return {
            "rows_in": self.rows_in,
            "rows_out": self.rows_out,
            "duplicates_removed": self.duplicates_removed,
            "nulls_filled": self.nulls_filled,
            "outliers_flagged": self.outliers_flagged,
        }

    def drop_missing_identifiers(self) -> "DataCleaner":
        """Drop records missing mandatory student_id."""
        if "student_id" in self._df.columns:
            # Replace empty strings or whitespace with NaN
            self._df["student_id"] = self._df["student_id"].replace(r"^\s*$", np.nan, regex=True)
            initial_count = len(self._df)
            self._df = self._df.dropna(subset=["student_id"]).reset_index(drop=True)
            # If student_id is numeric string, cast to int
            try:
                self._df["student_id"] = self._df["student_id"].astype(int)
            except (ValueError, TypeError):
                pass
        return self

    def drop_duplicates(self) -> "DataCleaner":
        """Drop duplicate rows by email or composite key (student_id, course_code, semester)."""
        initial_count = len(self._df)

        # Check composite course enrollment duplicate if columns exist
        subset_cols = []
        if all(c in self._df.columns for c in ["student_id", "course_code", "semester"]):
            subset_cols = ["student_id", "course_code", "semester"]
        elif "email" in self._df.columns and "course_code" in self._df.columns:
            subset_cols = ["email", "course_code"]
        elif "email" in self._df.columns:
            subset_cols = ["email"]
        elif "student_id" in self._df.columns:
            subset_cols = ["student_id"]

        if subset_cols:
            self._df = self._df.drop_duplicates(subset=subset_cols, keep="first").reset_index(drop=True)

        self.duplicates_removed += initial_count - len(self._df)
        return self

    def clean_names_and_emails(self) -> "DataCleaner":
        """Strip and title-case names, lowercase emails, and validate format."""
        if "first_name" in self._df.columns:
            self._df["first_name"] = (
                self._df["first_name"]
                .astype(str)
                .apply(clean_name)
            )

        if "last_name" in self._df.columns:
            self._df["last_name"] = (
                self._df["last_name"]
                .astype(str)
                .apply(clean_name)
            )

        if "email" in self._df.columns:
            self._df["email"] = (
                self._df["email"]
                .astype(str)
                .str.strip()
                .str.lower()
            )
            # Filter out records with invalid emails
            valid_mask = self._df["email"].apply(is_valid_email)
            self._df = self._df[valid_mask].reset_index(drop=True)

        return self

    def cast_types_and_parse_dates(self) -> "DataCleaner":
        """Cast dtypes and parse dates consistently."""
        if "dob" in self._df.columns:
            self._df["dob"] = self._df["dob"].apply(parse_date)

        # Cast admission_year
        if "admission_year" in self._df.columns:
            self._df["admission_year"] = pd.to_numeric(
                self._df["admission_year"], errors="coerce"
            ).fillna(2022).astype(int)

        # Cast semester
        if "semester" in self._df.columns:
            self._df["semester"] = pd.to_numeric(
                self._df["semester"], errors="coerce"
            ).fillna(1).astype(int)

        # Cast credits
        if "credits" in self._df.columns:
            self._df["credits"] = pd.to_numeric(
                self._df["credits"], errors="coerce"
            ).fillna(3).astype(int)

        # Gender normalization (default to 'O' if invalid)
        if "gender" in self._df.columns:
            self._df["gender"] = (
                self._df["gender"]
                .astype(str)
                .str.strip()
                .str.upper()
                .apply(lambda g: g if g in ("M", "F", "O") else "O")
            )

        return self

    def clean_scores_and_attendance(self) -> "DataCleaner":
        """Clip marks and attendance to 0-100; null out impossible values."""
        if "marks" in self._df.columns:
            self._df["marks"] = pd.to_numeric(self._df["marks"], errors="coerce")
            # Null out impossible values: e.g. < -10 or > 150 treated as corrupt / null
            impossible_mask = (self._df["marks"] < 0) | (self._df["marks"] > 100)
            # Clip values within reasonable bounds (e.g. -5 to 105) to 0-100, null out extreme outliers
            extreme_mask = (self._df["marks"] < -10) | (self._df["marks"] > 150)
            self._df.loc[extreme_mask, "marks"] = np.nan
            self._df["marks"] = self._df["marks"].clip(lower=0.0, upper=100.0)

        if "attendance_pct" in self._df.columns:
            self._df["attendance_pct"] = pd.to_numeric(self._df["attendance_pct"], errors="coerce")
            extreme_att = (self._df["attendance_pct"] < -10) | (self._df["attendance_pct"] > 150)
            self._df.loc[extreme_att, "attendance_pct"] = np.nan
            self._df["attendance_pct"] = self._df["attendance_pct"].clip(lower=0.0, upper=100.0)

        return self

    def impute_missing_marks(self) -> "DataCleaner":
        """Impute missing marks with the course median; fallback to overall median."""
        if "marks" in self._df.columns:
            initial_nulls = self._df["marks"].isna().sum()
            if initial_nulls > 0:
                if "course_code" in self._df.columns:
                    course_medians = self._df.groupby("course_code")["marks"].transform("median")
                    self._df["marks"] = self._df["marks"].fillna(course_medians)

                # Fallback to overall median or default passing grade
                overall_median = self._df["marks"].median()
                if np.isnan(overall_median):
                    overall_median = 50.0
                self._df["marks"] = self._df["marks"].fillna(overall_median)

                remaining_nulls = self._df["marks"].isna().sum()
                self.nulls_filled += int(initial_nulls - remaining_nulls)

        if "attendance_pct" in self._df.columns:
            att_nulls = self._df["attendance_pct"].isna().sum()
            if att_nulls > 0:
                dept_att = self._df["attendance_pct"].median()
                if np.isnan(dept_att):
                    dept_att = 75.0
                self._df["attendance_pct"] = self._df["attendance_pct"].fillna(dept_att)
                self.nulls_filled += int(att_nulls)

        return self

    def flag_outliers_iqr(self, column: str = "marks") -> "DataCleaner":
        """Flag outliers using NumPy IQR without deleting rows, storing in is_outlier column."""
        self._df["is_outlier"] = False
        if column in self._df.columns and len(self._df) > 4:
            valid_series = self._df[column].dropna()
            if not valid_series.empty:
                q25, q75 = np.percentile(valid_series, [25, 75])
                iqr = q75 - q25
                lower_bound = q25 - 1.5 * iqr
                upper_bound = q75 + 1.5 * iqr

                outlier_mask = (self._df[column] < lower_bound) | (self._df[column] > upper_bound)
                self._df["is_outlier"] = outlier_mask
                self.outliers_flagged = int(outlier_mask.sum())

        return self

    def clean_all(self) -> "DataCleaner":
        """Execute full cleaning pipeline in optimal order."""
        return (
            self.drop_missing_identifiers()
            .drop_duplicates()
            .clean_names_and_emails()
            .cast_types_and_parse_dates()
            .clean_scores_and_attendance()
            .impute_missing_marks()
            .flag_outliers_iqr()
        )
