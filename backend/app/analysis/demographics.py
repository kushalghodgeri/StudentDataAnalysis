"""DemographicsAnalyzer calculating student population distributions."""

from typing import Any, Dict
import pandas as pd
from app.analysis.base_analyzer import BaseAnalyzer


class DemographicsAnalyzer(BaseAnalyzer):
    """Analyzes student demographics including gender representation, department headcounts, and cohorts."""

    def analyze(self) -> Dict[str, Any]:
        """Compute demographic breakdowns and return a JSON-serializable dictionary."""
        if self.df.empty:
            return self._empty_response()

        # Deduplicate students if enrollment joined data is passed
        student_df = self.df
        if "student_id" in self.df.columns:
            student_df = self.df.drop_duplicates(subset=["student_id"])
        elif "email" in self.df.columns:
            student_df = self.df.drop_duplicates(subset=["email"])

        # 1. Gender Breakdown
        gender_counts = {}
        if "gender" in student_df.columns:
            g_counts = student_df["gender"].value_counts()
            gender_counts = {str(k): int(v) for k, v in g_counts.to_dict().items()}

        # 2. Department Headcounts
        dept_counts = {}
        if "department" in student_df.columns:
            d_counts = student_df["department"].value_counts()
            dept_counts = {str(k): int(v) for k, v in d_counts.to_dict().items()}

        # 3. Admission Year Cohorts
        cohorts = {}
        if "admission_year" in student_df.columns:
            c_counts = student_df["admission_year"].value_counts().sort_index()
            cohorts = {str(k): int(v) for k, v in c_counts.to_dict().items()}

        return {
            "gender": gender_counts,
            "department_counts": dept_counts,
            "cohorts": cohorts,
        }

    def _empty_response(self) -> Dict[str, Any]:
        return {
            "gender": {},
            "department_counts": {},
            "cohorts": {},
        }
