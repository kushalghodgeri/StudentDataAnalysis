"""AttendanceAnalyzer computing departmental attendance, correlations, and at-risk students."""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from app.analysis.base_analyzer import BaseAnalyzer


class AttendanceAnalyzer(BaseAnalyzer):
    """Analyzes attendance patterns, attendance-marks correlation, and flagged at-risk students."""

    def analyze(self) -> Dict[str, Any]:
        """Compute attendance analytics and return a JSON-serializable dictionary."""
        if self.df.empty:
            return self._empty_response()

        # 1. Department Attendance Averages
        by_department = {}
        if "department" in self.df.columns and "attendance_pct" in self.df.columns:
            valid_att = self.df.dropna(subset=["attendance_pct"])
            if not valid_att.empty:
                dept_grp = valid_att.groupby("department")["attendance_pct"].mean().round(2)
                by_department = {str(k): float(v) for k, v in dept_grp.to_dict().items()}

        # 2. Pearson Correlation (attendance vs marks) via np.corrcoef
        correlation = self._compute_correlation()

        # 3. At-Risk Student List (attendance < 75% and marks < 40)
        at_risk = self._find_at_risk_students()

        return {
            "by_department": by_department,
            "correlation": correlation,
            "at_risk": at_risk,
        }

    def _compute_correlation(self) -> Optional[float]:
        """Calculate Pearson correlation between attendance_pct and marks using NumPy."""
        if "attendance_pct" not in self.df.columns or "marks" not in self.df.columns:
            return None

        paired = self.df.dropna(subset=["attendance_pct", "marks"])
        if len(paired) < 2:
            return None

        att_vals = paired["attendance_pct"].astype(float).values
        marks_vals = paired["marks"].astype(float).values

        # Check for zero variance to avoid divide-by-zero warnings
        if np.std(att_vals) == 0 or np.std(marks_vals) == 0:
            return 0.0

        corr_matrix = np.corrcoef(att_vals, marks_vals)
        corr_val = float(corr_matrix[0, 1])
        if np.isnan(corr_val):
            return 0.0
        return round(corr_val, 4)

    def _find_at_risk_students(self) -> List[Dict[str, Any]]:
        """Identify enrollments meeting both criteria: attendance < 75% and marks < 40."""
        if "attendance_pct" not in self.df.columns or "marks" not in self.df.columns:
            return []

        risk_mask = (self.df["attendance_pct"] < 75.0) & (self.df["marks"] < 40.0)
        risk_df = self.df[risk_mask].copy()

        if risk_df.empty:
            return []

        # Resolve full_name
        if "full_name" not in risk_df.columns:
            if "first_name" in risk_df.columns and "last_name" in risk_df.columns:
                risk_df["full_name"] = risk_df["first_name"].astype(str) + " " + risk_df["last_name"].astype(str)
            elif "student_id" in risk_df.columns:
                risk_df["full_name"] = "Student " + risk_df["student_id"].astype(str)
            else:
                risk_df["full_name"] = "Unknown Student"

        results = []
        for _, r in risk_df.iterrows():
            results.append({
                "student_id": int(r.get("student_id", 0)),
                "full_name": str(r.get("full_name", "")),
                "department": str(r.get("department", "N/A")),
                "semester": int(r.get("semester", 1)),
                "course_code": str(r.get("course_code", "N/A")),
                "marks": round(float(r.get("marks", 0.0)), 2),
                "attendance_pct": round(float(r.get("attendance_pct", 0.0)), 2),
            })

        # Sort by lowest marks first
        results.sort(key=lambda x: (x["marks"], x["attendance_pct"]))
        return results

    def _empty_response(self) -> Dict[str, Any]:
        return {
            "by_department": {},
            "correlation": None,
            "at_risk": [],
        }
