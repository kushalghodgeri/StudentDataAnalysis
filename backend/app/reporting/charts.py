"""ChartBuilder generating publication-ready data visualizations using Matplotlib (Agg backend)."""

import os
from pathlib import Path
from typing import Dict, List, Optional

# Ensure matplotlib cache directory is inside the workspace to avoid Windows permission issues
if "MPLCONFIGDIR" not in os.environ:
    mpl_cache = Path(__file__).resolve().parent.parent.parent / ".mpl_cache"
    mpl_cache.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(mpl_cache)

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from app.config.settings import get_settings
from app.utils.logger import logger


class ChartBuilder:
    """Builder producing static analysis charts saved as PNG images."""

    # Cohesive corporate color palette
    COLORS = {
        "primary": "#1f77b4",
        "secondary": "#2ca02c",
        "accent": "#ff7f0e",
        "danger": "#d62728",
        "neutral": "#7f7f7f",
        "palette": ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD"],
    }

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or get_settings().charts_dir_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Apply standard plot formatting
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "figure.autolayout": True,
        })

    def department_avg_bar(self, df: pd.DataFrame, filename: str = "department_avg_bar.png") -> Path:
        """Bar chart illustrating mean student marks across departments."""
        out_path = self.output_dir / filename
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)

        if not df.empty and "department" in df.columns and "marks" in df.columns:
            dept_avgs = df.groupby("department")["marks"].mean().sort_values(ascending=False)
            bars = ax.bar(dept_avgs.index, dept_avgs.values, color=self.COLORS["palette"][:len(dept_avgs)])
            ax.set_title("Average Marks by Department", pad=12, fontweight="bold")
            ax.set_xlabel("Department")
            ax.set_ylabel("Average Marks (out of 100)")
            ax.set_ylim(0, 100)
            plt.xticks(rotation=20, ha="right")

            # Value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontweight="semibold",
                )
        else:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")

        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def marks_histogram(self, df: pd.DataFrame, filename: str = "marks_histogram.png") -> Path:
        """Histogram showing frequency distribution of marks with mean and median indicators."""
        out_path = self.output_dir / filename
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)

        if not df.empty and "marks" in df.columns:
            marks = df["marks"].dropna()
            n, bins, patches = ax.hist(
                marks, bins=15, range=(0, 100), color="#4C72B0", edgecolor="white", alpha=0.85
            )
            mean_val = marks.mean()
            median_val = marks.median()

            ax.axvline(mean_val, color="#C44E52", linestyle="--", linewidth=1.5, label=f"Mean: {mean_val:.1f}")
            ax.axvline(median_val, color="#2ca02c", linestyle="-.", linewidth=1.5, label=f"Median: {median_val:.1f}")
            ax.axvline(40, color="#ff7f0e", linestyle=":", linewidth=1.5, label="Pass Mark (40)")

            ax.set_title("Distribution of Student Marks", pad=12, fontweight="bold")
            ax.set_xlabel("Marks")
            ax.set_ylabel("Number of Students")
            ax.set_xlim(0, 100)
            ax.legend(loc="upper left")
        else:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")

        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def course_boxplot(self, df: pd.DataFrame, filename: str = "course_boxplot.png") -> Path:
        """Boxplot capturing marks spread and variability across top courses."""
        out_path = self.output_dir / filename
        fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)

        if not df.empty and "course_code" in df.columns and "marks" in df.columns:
            # Pick top courses by enrollment
            top_courses = df["course_code"].value_counts().head(8).index.tolist()
            filtered = df[df["course_code"].isin(top_courses)]
            grouped_data = [filtered[filtered["course_code"] == c]["marks"].dropna() for c in top_courses]

            bp = ax.boxplot(
                grouped_data,
                tick_labels=top_courses,
                patch_artist=True,
                boxprops=dict(facecolor="#8172B2", alpha=0.7),
                medianprops=dict(color="#d62728", linewidth=1.5),
            )
            ax.set_title("Marks Dispersion by Course (Top Courses)", pad=12, fontweight="bold")
            ax.set_xlabel("Course Code")
            ax.set_ylabel("Marks")
            ax.set_ylim(0, 105)
            plt.xticks(rotation=25, ha="right")
        else:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")

        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def semester_trend_line(self, df: pd.DataFrame, filename: str = "semester_trend_line.png") -> Path:
        """Line chart tracing academic performance trends over consecutive semesters."""
        out_path = self.output_dir / filename
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)

        if not df.empty and "semester" in df.columns and "marks" in df.columns:
            sem_stats = df.groupby("semester")["marks"].agg(["mean", "median"]).sort_index()
            ax.plot(
                sem_stats.index,
                sem_stats["mean"],
                marker="o",
                linewidth=2.2,
                color="#4C72B0",
                label="Average Marks",
            )
            ax.plot(
                sem_stats.index,
                sem_stats["median"],
                marker="s",
                linestyle="--",
                linewidth=1.8,
                color="#55A868",
                label="Median Marks",
            )

            ax.set_title("Performance Trend Across Semesters", pad=12, fontweight="bold")
            ax.set_xlabel("Semester")
            ax.set_ylabel("Marks")
            ax.set_ylim(0, 100)
            ax.set_xticks(sem_stats.index)
            ax.legend(loc="lower right")
        else:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")

        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def attendance_vs_marks_scatter(
        self, df: pd.DataFrame, filename: str = "attendance_vs_marks_scatter.png"
    ) -> Path:
        """Scatter plot correlating attendance with marks, complete with linear trendline."""
        out_path = self.output_dir / filename
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)

        if not df.empty and "attendance_pct" in df.columns and "marks" in df.columns:
            clean = df.dropna(subset=["attendance_pct", "marks"])
            x = clean["attendance_pct"].astype(float).values
            y = clean["marks"].astype(float).values

            ax.scatter(x, y, alpha=0.45, color="#4C72B0", edgecolors="none", s=30, label="Student Enrollment")

            # Calculate and plot trendline if points exist
            if len(x) > 1 and np.std(x) > 0:
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                x_vals = np.linspace(x.min(), x.max(), 100)
                ax.plot(
                    x_vals,
                    p(x_vals),
                    color="#C44E52",
                    linewidth=2,
                    label=f"Trendline (slope: {z[0]:.2f})",
                )

            # Risk quadrant indicator lines
            ax.axvline(75, color="#ff7f0e", linestyle=":", alpha=0.7)
            ax.axhline(40, color="#d62728", linestyle=":", alpha=0.7)
            ax.text(5, 5, "At-Risk Zone\n(<75% Att, <40 Marks)", color="#d62728", fontsize=8, alpha=0.8)

            ax.set_title("Attendance vs. Academic Marks Correlation", pad=12, fontweight="bold")
            ax.set_xlabel("Attendance (%)")
            ax.set_ylabel("Marks (out of 100)")
            ax.set_xlim(0, 105)
            ax.set_ylim(0, 105)
            ax.legend(loc="upper left")
        else:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")

        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def grade_donut(self, df: pd.DataFrame, filename: str = "grade_donut.png") -> Path:
        """Donut chart illustrating relative proportion of student grade tiers."""
        out_path = self.output_dir / filename
        fig, ax = plt.subplots(figsize=(6, 5), dpi=150)

        if not df.empty and "marks" in df.columns:
            bins = [-np.inf, 39.99, 54.99, 69.99, 84.99, np.inf]
            labels = ["F (<40)", "D (40-54)", "C (55-69)", "B (70-84)", "A (>=85)"]
            cats = pd.cut(df["marks"], bins=bins, labels=labels)
            counts = cats.value_counts()[labels]

            colors = ["#d62728", "#ff7f0e", "#bcbd22", "#2ca02c", "#1f77b4"]
            # Exclude zeros from wedge
            non_zero = counts[counts > 0]
            if not non_zero.empty:
                wedges, texts, autotexts = ax.pie(
                    non_zero,
                    labels=non_zero.index,
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=[colors[labels.index(i)] for i in non_zero.index],
                    wedgeprops=dict(width=0.4, edgecolor="white"),
                    pctdistance=0.75,
                )
                plt.setp(autotexts, size=8, weight="bold")
                ax.set_title("Grade Band Distribution", pad=12, fontweight="bold")
            else:
                ax.text(0.5, 0.5, "No Grade Data", ha="center", va="center")
        else:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")

        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def dept_course_heatmap(self, df: pd.DataFrame, filename: str = "dept_course_heatmap.png") -> Path:
        """Heatmap displaying average marks across departments and popular courses."""
        out_path = self.output_dir / filename
        fig, ax = plt.subplots(figsize=(8.5, 5), dpi=150)

        if not df.empty and all(c in df.columns for c in ["department", "course_code", "marks"]):
            # Pivot table department vs top 6 courses
            top_courses = df["course_code"].value_counts().head(6).index.tolist()
            sub = df[df["course_code"].isin(top_courses)]
            pivot = sub.pivot_table(index="department", columns="course_code", values="marks", aggfunc="mean").round(1)

            if not pivot.empty:
                im = ax.imshow(pivot.values, cmap="YlGnBu", aspect="auto", vmin=30, vmax=95)
                cbar = fig.colorbar(im, ax=ax)
                cbar.set_label("Mean Marks", rotation=270, labelpad=12)

                ax.set_xticks(np.arange(len(pivot.columns)))
                ax.set_yticks(np.arange(len(pivot.index)))
                ax.set_xticklabels(pivot.columns, rotation=25, ha="right")
                ax.set_yticklabels(pivot.index)

                # Text annotations in each cell
                for i in range(len(pivot.index)):
                    for j in range(len(pivot.columns)):
                        val = pivot.iloc[i, j]
                        if not np.isnan(val):
                            color = "white" if val > 65 else "black"
                            ax.text(j, i, f"{val:.1f}", ha="center", va="center", color=color, fontsize=8)

                ax.set_title("Performance Heatmap: Department vs Course", pad=12, fontweight="bold")
            else:
                ax.text(0.5, 0.5, "Insufficient Pivot Data", ha="center", va="center")
        else:
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")

        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def generate_all(self, df: pd.DataFrame, prefix: str = "") -> List[Path]:
        """Generate all 7 analytical charts with an optional prefix tag."""
        prefix_str = f"{prefix}_" if prefix else ""
        return [
            self.department_avg_bar(df, f"{prefix_str}department_avg_bar.png"),
            self.marks_histogram(df, f"{prefix_str}marks_histogram.png"),
            self.course_boxplot(df, f"{prefix_str}course_boxplot.png"),
            self.semester_trend_line(df, f"{prefix_str}semester_trend_line.png"),
            self.attendance_vs_marks_scatter(df, f"{prefix_str}attendance_vs_marks_scatter.png"),
            self.grade_donut(df, f"{prefix_str}grade_donut.png"),
            self.dept_course_heatmap(df, f"{prefix_str}dept_course_heatmap.png"),
        ]
