"""PerformanceAnalyzer computing academic metrics, letter grades, trends, and rankings."""

from typing import Any, Dict, List
import numpy as np
import pandas as pd
from app.analysis.base_analyzer import BaseAnalyzer


class PerformanceAnalyzer(BaseAnalyzer):
    """Analyzes academic marks, grade bands, departmental performance, and student rankings."""

    def analyze(self) -> Dict[str, Any]:
        """Compute performance statistics and return a JSON-serializable dictionary."""
        if self.df.empty or "marks" not in self.df.columns:
            return self._empty_response()

        valid_df = self.df.dropna(subset=["marks"]).copy()
        if valid_df.empty:
            return self._empty_response()

        marks_series = valid_df["marks"].astype(float)
        count = int(len(marks_series))
        mean_val = round(float(marks_series.mean()), 2)
        median_val = round(float(marks_series.median()), 2)
        std_val = round(float(marks_series.std()), 2) if count > 1 else 0.0
        min_val = round(float(marks_series.min()), 2)
        max_val = round(float(marks_series.max()), 2)

        # Percentiles using NumPy
        p25, p50, p75, p90 = [
            round(float(x), 2)
            for x in np.percentile(marks_series, [25, 50, 75, 90])
        ]

        # Pass rate (marks >= 40)
        passed_count = int((marks_series >= 40.0).sum())
        pass_rate = round((passed_count / count) * 100.0, 2)

        stats = {
            "count": count,
            "mean": mean_val,
            "median": median_val,
            "std": std_val,
            "min": min_val,
            "max": max_val,
            "percentiles": {
                "p25": p25,
                "p50": p50,
                "p75": p75,
                "p90": p90,
            },
            "pass_rate": pass_rate,
        }

        # Grade distribution using pd.cut (A: >=85, B: 70-84, C: 55-69, D: 40-54, F: <40)
        grade_dist = self._compute_grade_distribution(valid_df)

        # Department-wise averages
        dept_averages = {}
        if "department" in valid_df.columns:
            dept_grp = valid_df.groupby("department")["marks"].mean().round(2)
            dept_averages = {str(k): float(v) for k, v in dept_grp.to_dict().items()}

        # Semester-wise averages
        semester_trend = {}
        if "semester" in valid_df.columns:
            sem_grp = valid_df.groupby("semester")["marks"].mean().round(2)
            semester_trend = {f"Sem {k}": float(v) for k, v in sem_grp.to_dict().items()}

        # Top 10 and Bottom 10 students
        top10, bottom10 = self._compute_rankings(valid_df)

        return {
            "stats": stats,
            "grade_distribution": grade_dist,
            "dept_averages": dept_averages,
            "semester_trend": semester_trend,
            "top10": top10,
            "bottom10": bottom10,
        }

    def _compute_grade_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Categorize marks into standard A/B/C/D/F grades using pd.cut."""
        bins = [-np.inf, 39.99, 54.99, 69.99, 84.99, np.inf]
        labels = ["F", "D", "C", "B", "A"]
        categorized = pd.cut(df["marks"], bins=bins, labels=labels, right=True)
        counts = categorized.value_counts()
        return {label: int(counts.get(label, 0)) for label in ["A", "B", "C", "D", "F"]}

    def _compute_rankings(
        self, df: pd.DataFrame, limit: int = 10
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extract top and bottom performing students."""
        group_cols = ["student_id"]
        for col in ["full_name", "first_name", "last_name", "department"]:
            if col in df.columns:
                group_cols.append(col)

        # Ensure student_id exists
        if "student_id" not in df.columns:
            return [], []

        agg_dict = {"marks": ["mean", "count"]}
        grouped = df.groupby(group_cols).agg(agg_dict)
        grouped.columns = ["marks_avg", "enrolled_courses"]
        grouped = grouped.reset_index()
        grouped["marks_avg"] = grouped["marks_avg"].round(2)

        # Resolve full_name
        if "full_name" not in grouped.columns:
            if "first_name" in grouped.columns and "last_name" in grouped.columns:
                grouped["full_name"] = grouped["first_name"] + " " + grouped["last_name"]
            else:
                grouped["full_name"] = "Student " + grouped["student_id"].astype(str)

        if "department" not in grouped.columns:
            grouped["department"] = "N/A"

        # Top 10
        top_df = grouped.sort_values(by="marks_avg", ascending=False).head(limit)
        bottom_df = grouped.sort_values(by="marks_avg", ascending=True).head(limit)

        def to_items(sub_df):
            return [
                {
                    "student_id": int(r["student_id"]),
                    "full_name": str(r["full_name"]),
                    "department": str(r["department"]),
                    "marks_avg": float(r["marks_avg"]),
                    "enrolled_courses": int(r["enrolled_courses"]),
                }
                for _, r in sub_df.iterrows()
            ]

        return to_items(top_df), to_items(bottom_df)

    def _empty_response(self) -> Dict[str, Any]:
        return {
            "stats": {
                "count": 0,
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
                "percentiles": {"p25": None, "p50": None, "p75": None, "p90": None},
                "pass_rate": None,
            },
            "grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
            "dept_averages": {},
            "semester_trend": {},
            "top10": [],
            "bottom10": [],
        }
