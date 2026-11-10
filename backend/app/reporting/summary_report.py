"""SummaryReport generating CSV, multi-tab Excel, and comprehensive multi-page PDF documents."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

from app.config.settings import get_settings
from app.reporting.base_report import BaseReport
from app.reporting.charts import ChartBuilder
from app.utils.logger import logger


class SummaryReport(BaseReport):
    """Generates structured CSV, Excel workbooks, and polished multi-page PDF executive summaries."""

    def __init__(
        self,
        df: pd.DataFrame,
        overview_stats: Optional[Dict[str, Any]] = None,
        performance_data: Optional[Dict[str, Any]] = None,
        attendance_data: Optional[Dict[str, Any]] = None,
        report_id: Optional[str] = None,
        output_dir: Optional[Path] = None,
        semester: Optional[int] = None,
        department: Optional[str] = None,
    ):
        self.df = df.copy() if df is not None else pd.DataFrame()
        self.overview = overview_stats or {}
        self.performance = performance_data or {}
        self.attendance = attendance_data or {}
        self.report_id = report_id or f"rep_{uuid.uuid4().hex[:8]}"
        self.output_dir = output_dir or get_settings().reports_dir_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.semester = semester
        self.department = department
        self.chart_builder = ChartBuilder(get_settings().charts_dir_path)

    def generate(self, formats: Optional[List[str]] = None) -> Dict[str, Path]:
        """Generate reports in requested formats (csv, xlsx, pdf)."""
        target_formats = [f.lower().strip() for f in (formats or ["pdf", "csv", "xlsx"])]
        generated_files: Dict[str, Path] = {}

        if "csv" in target_formats:
            generated_files["csv"] = self._generate_csv()

        if "xlsx" in target_formats:
            generated_files["xlsx"] = self._generate_excel()

        if "pdf" in target_formats:
            generated_files["pdf"] = self._generate_pdf()

        return generated_files

    def _generate_csv(self) -> Path:
        """Export cleaned tabular dataset as CSV."""
        filename = f"report_{self.report_id}.csv"
        out_path = self.output_dir / filename
        export_df = self.df.copy()
        export_df.to_csv(out_path, index=False, encoding="utf-8")
        logger.info(f"Generated CSV report at {out_path}")
        return out_path

    def _generate_excel(self) -> Path:
        """Generate an Excel workbook with dedicated analytical tabs."""
        filename = f"report_{self.report_id}.xlsx"
        out_path = self.output_dir / filename

        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            # 1. Executive Summary Sheet
            overview_rows = [
                {"Metric": "Report ID", "Value": self.report_id},
                {"Metric": "Generated Date", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                {"Metric": "Semester Filter", "Value": str(self.semester) if self.semester else "All"},
                {"Metric": "Department Filter", "Value": self.department or "All"},
                {"Metric": "Total Students", "Value": self.overview.get("total_students", len(self.df["student_id"].unique()) if "student_id" in self.df.columns else 0)},
                {"Metric": "Total Courses", "Value": self.overview.get("total_courses", len(self.df["course_id"].unique()) if "course_id" in self.df.columns else 0)},
                {"Metric": "Average Marks", "Value": self.overview.get("avg_marks", round(float(self.df["marks"].mean()), 2) if "marks" in self.df.columns and not self.df["marks"].empty else "N/A")},
                {"Metric": "Average Attendance (%)", "Value": self.overview.get("avg_attendance", round(float(self.df["attendance_pct"].mean()), 2) if "attendance_pct" in self.df.columns and not self.df["attendance_pct"].empty else "N/A")},
                {"Metric": "Pass Rate (%)", "Value": self.overview.get("pass_rate", "N/A")},
                {"Metric": "At-Risk Enrollments", "Value": self.overview.get("at_risk_count", len(self.attendance.get("at_risk", [])))},
            ]
            pd.DataFrame(overview_rows).to_excel(writer, sheet_name="Executive Summary", index=False)

            # 2. Raw Enrollment Details
            if not self.df.empty:
                self.df.to_excel(writer, sheet_name="Enrollment Data", index=False)

            # 3. Department & Grade Analysis
            if "dept_averages" in self.performance:
                dept_df = pd.DataFrame([
                    {"Department": d, "Mean Marks": m}
                    for d, m in self.performance["dept_averages"].items()
                ])
                dept_df.to_excel(writer, sheet_name="Department Stats", index=False)

            # 4. At-Risk Students Registry
            at_risk_list = self.attendance.get("at_risk", [])
            if at_risk_list:
                pd.DataFrame(at_risk_list).to_excel(writer, sheet_name="At Risk Students", index=False)

        logger.info(f"Generated Excel workbook at {out_path}")
        return out_path

    def _generate_pdf(self) -> Path:
        """Create a multi-page executive PDF report using PdfPages and Matplotlib."""
        filename = f"report_{self.report_id}.pdf"
        out_path = self.output_dir / filename

        with PdfPages(out_path) as pdf:
            # Page 1: Title and Executive KPI Dashboard
            self._render_pdf_cover_page(pdf)

            # Page 2: Department Performance & Grade Donut
            self._render_pdf_page_charts(
                pdf,
                chart_fn_1=self.chart_builder.department_avg_bar,
                chart_fn_2=self.chart_builder.grade_donut,
                page_title="Department Breakdown & Grade Tier Distribution",
            )

            # Page 3: Distribution & Correlation
            self._render_pdf_page_charts(
                pdf,
                chart_fn_1=self.chart_builder.marks_histogram,
                chart_fn_2=self.chart_builder.attendance_vs_marks_scatter,
                page_title="Marks Spread & Attendance Correlation",
            )

            # Page 4: Dispersion Boxplot & Heatmap
            self._render_pdf_page_charts(
                pdf,
                chart_fn_1=self.chart_builder.course_boxplot,
                chart_fn_2=self.chart_builder.dept_course_heatmap,
                page_title="Course Dispersion & Cross-Departmental Heatmap",
            )

            # Page 5: At-Risk Action List
            self._render_pdf_at_risk_page(pdf)

        logger.info(f"Generated PDF report at {out_path}")
        return out_path

    def _render_pdf_cover_page(self, pdf: PdfPages) -> None:
        """Cover page detailing executive KPIs in tabular card style."""
        fig, ax = plt.subplots(figsize=(8.5, 11), dpi=150)
        ax.axis("off")

        # Header Banner
        ax.text(0.5, 0.92, "STUDENT DATA ANALYSIS & REPORTING SYSTEM", fontsize=18, fontweight="bold", ha="center", color="#1f77b4")
        ax.text(0.5, 0.88, "Comprehensive Academic Performance & Ingestion Report", fontsize=12, fontstyle="italic", ha="center", color="#555555")
        ax.axhline(0.85, 0.05, 0.95, color="#1f77b4", linewidth=2)

        # Meta Information Block
        meta_text = (
            f"Report ID: {self.report_id}\n"
            f"Generated On: {datetime.now().strftime('%B %d, %Y - %H:%M:%S')}\n"
            f"Semester Filter: {self.semester or 'All Semesters'}\n"
            f"Department Filter: {self.department or 'All Departments'}\n"
            f"Total Processed Records: {len(self.df)}"
        )
        ax.text(0.1, 0.77, meta_text, fontsize=10, linespacing=1.6, bbox=dict(boxstyle="round,pad=0.8", facecolor="#f4f6f9", edgecolor="#d1d5db"))

        # Executive KPI Cards (drawn as a table)
        kpi_data = [
            ["Key Performance Indicator", "Value", "Benchmark Status"],
            ["Total Enrolled Students", str(self.overview.get("total_students", len(self.df["student_id"].unique()) if "student_id" in self.df.columns else 0)), "Active Cohort"],
            ["Total Evaluated Courses", str(self.overview.get("total_courses", len(self.df["course_id"].unique()) if "course_id" in self.df.columns else 0)), "Curriculum"],
            ["Mean Academic Marks", f"{self.overview.get('avg_marks', 'N/A')}/100", "Satisfactory"],
            ["Mean Attendance", f"{self.overview.get('avg_attendance', 'N/A')}%", "Target: >=80%"],
            ["Cohort Pass Rate", f"{self.overview.get('pass_rate', 'N/A')}%", "Target: >=85%"],
            ["Flagged At-Risk Students", str(self.overview.get("at_risk_count", len(self.attendance.get("at_risk", [])))), "Requires Intervention" if self.overview.get("at_risk_count", 0) > 0 else "Normal"],
        ]

        table = ax.table(
            cellText=kpi_data[1:],
            colLabels=kpi_data[0],
            loc="center",
            cellLoc="center",
            bbox=[0.08, 0.35, 0.84, 0.32],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9.5)
        table.scale(1.0, 1.8)

        # Style header row
        for i in range(3):
            table[(0, i)].set_facecolor("#1f77b4")
            table[(0, i)].set_text_props(color="white", weight="bold")

        # Footer notes
        footer_note = (
            "Notice: This report is automatically generated by the Student Data Analysis backend pipeline.\n"
            "At-Risk status is flagged when a student's attendance falls below 75% AND academic marks fall below 40."
        )
        ax.text(0.5, 0.12, footer_note, fontsize=8.5, ha="center", color="#777777", linespacing=1.4)

        pdf.savefig(fig)
        plt.close(fig)

    def _render_pdf_page_charts(
        self, pdf: PdfPages, chart_fn_1, chart_fn_2, page_title: str
    ) -> None:
        """Render two stacked analytical charts on a single letter-sized PDF page."""
        fig = plt.figure(figsize=(8.5, 11), dpi=150)
        fig.suptitle(page_title, fontsize=14, fontweight="bold", y=0.96)

        # Generate temporary chart images and draw onto figure
        tmp_id = uuid.uuid4().hex[:6]
        p1 = chart_fn_1(self.df, f"tmp_{tmp_id}_1.png")
        p2 = chart_fn_2(self.df, f"tmp_{tmp_id}_2.png")

        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        try:
            img1 = plt.imread(str(p1))
            ax1.imshow(img1)
            ax1.axis("off")

            img2 = plt.imread(str(p2))
            ax2.imshow(img2)
            ax2.axis("off")

            fig.tight_layout(rect=[0.05, 0.03, 0.95, 0.94])
            pdf.savefig(fig)
        finally:
            plt.close(fig)
            p1.unlink(missing_ok=True)
            p2.unlink(missing_ok=True)

    def _render_pdf_at_risk_page(self, pdf: PdfPages) -> None:
        """Render table of top at-risk students for academic counseling."""
        fig, ax = plt.subplots(figsize=(8.5, 11), dpi=150)
        ax.axis("off")

        ax.text(0.5, 0.94, "Action Required: At-Risk Student Registry", fontsize=15, fontweight="bold", ha="center", color="#d62728")
        ax.text(0.5, 0.90, "Identified enrollments with Attendance < 75% and Marks < 40", fontsize=10, fontstyle="italic", ha="center")
        ax.axhline(0.88, 0.05, 0.95, color="#d62728", linewidth=1.5)

        at_risk_list = self.attendance.get("at_risk", [])
        if not at_risk_list:
            ax.text(0.5, 0.5, "No At-Risk Students Flagged in This Selection", ha="center", va="center", fontsize=12, color="#2ca02c")
        else:
            table_headers = ["Student ID", "Full Name", "Department", "Sem", "Course", "Marks", "Att %"]
            # Show up to top 20 at-risk students
            table_rows = []
            for item in at_risk_list[:20]:
                table_rows.append([
                    str(item["student_id"]),
                    str(item["full_name"])[:20],
                    str(item["department"])[:18],
                    str(item["semester"]),
                    str(item["course_code"]),
                    f"{item['marks']:.1f}",
                    f"{item['attendance_pct']:.1f}%",
                ])

            table = ax.table(
                cellText=table_rows,
                colLabels=table_headers,
                loc="upper center",
                cellLoc="center",
                bbox=[0.05, 0.15, 0.90, 0.70],
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8.5)
            table.scale(1.0, 1.4)

            # Style header
            for i in range(len(table_headers)):
                table[(0, i)].set_facecolor("#d62728")
                table[(0, i)].set_text_props(color="white", weight="bold")

        pdf.savefig(fig)
        plt.close(fig)
