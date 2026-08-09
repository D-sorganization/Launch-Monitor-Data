"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from launch_monitor_data.build import build_database
from launch_monitor_data.validation import validate_repository_data


def main() -> int:
    parser = argparse.ArgumentParser(prog="launch-monitor-data")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="Build CSV and SQLite artifacts")
    build.add_argument("--output", type=Path, default=Path("database"))
    subparsers.add_parser("validate", help="Validate source data and provenance")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            report = validate_repository_data()
            print(
                f"sources={report.source_count} "
                f"comparisons={report.comparison_count} "
                f"vendor_fields={report.vendor_field_count} ok={report.ok}"
            )
            for error in report.errors:
                print(f"ERROR: {error}")
            return 0 if report.ok else 1
        result = build_database(args.output)
    except (FileNotFoundError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(
        f"Built {result.observation_count} observations and "
        f"{result.reference_value_count} published reference values from "
        f"{result.source_count} registered sources in {result.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
