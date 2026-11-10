"""Command Line Interface for headless report compilation and scheduled automation."""

import argparse
import sys
from pathlib import Path

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config.settings import get_settings
from app.db.connection import DatabaseConnection
from app.services.pipeline import ReportPipeline
from app.utils.logger import logger


def parse_args():
    parser = argparse.ArgumentParser(
        prog="python -m app.cli",
        description="Headless Student Data Analysis and Reporting CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate analysis reports headlessly")
    report_parser.add_argument(
        "--semester",
        type=int,
        default=None,
        help="Filter by semester number (e.g., --semester 5)",
    )
    report_parser.add_argument(
        "--department",
        type=str,
        default=None,
        help="Optional filter by department name (e.g., --department 'Computer Science')",
    )
    report_parser.add_argument(
        "--formats",
        type=str,
        default="pdf,csv",
        help="Comma-separated output formats (e.g., --formats pdf,csv,xlsx)",
    )

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a raw dataset CSV/Excel file")
    ingest_parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to CSV or Excel dataset to ingest",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    db = DatabaseConnection()

    if args.command == "report":
        formats = [f.strip().lower() for f in args.formats.split(",") if f.strip()]
        logger.info(
            f"CLI: Running report generator for semester={args.semester}, "
            f"dept={args.department}, formats={formats}"
        )
        try:
            pipeline = ReportPipeline(db)
            result = pipeline.generate_report(
                semester=args.semester,
                department=args.department,
                formats=formats,
            )
            print("\n========================================================")
            print(" REPORT GENERATION COMPLETED SUCCESSFULLY")
            print("========================================================")
            print(f"Report ID: {result['report_id']}")
            print("\nGenerated Documents:")
            for f in result["files"]:
                print(f" - {f['name']} ({f['url']})")
            print("\nGenerated Charts:")
            for c in result["charts"]:
                print(f" - {c['name']}")
            print("========================================================\n")
            sys.exit(0)
        except Exception as e:
            logger.error(f"CLI Report generation failed: {e}")
            print(f"ERROR: Report generation failed: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "ingest":
        from pathlib import Path
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"ERROR: File {file_path} not found.", file=sys.stderr)
            sys.exit(1)

        try:
            pipeline = ReportPipeline(db)
            import_id, summary = pipeline.ingest_file(file_path, file_path.name)
            print(f"Import successful! Import ID: {import_id}")
            print(f"Summary: {summary}")
            sys.exit(0)
        except Exception as e:
            print(f"ERROR: Ingest failed: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
