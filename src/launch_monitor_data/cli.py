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
                f"vendor_fields={report.vendor_field_count} "
                f"qualified_sources={report.qualified_source_count} "
                f"qualified_rows={report.qualified_source_rows} "
                f"strict_model_inputs={report.strict_model_input_rows} "
                f"capability_schema={report.capability_schema} ok={report.ok}"
                f" release_b={report.release_b_analyzed_pairs}/"
                f"{report.release_b_planned_pairs} "
                f"release_b_triggered={report.release_b_triggered_pairs} "
                f"release_b_ready={report.release_b_confirmatory_ready} "
                f"vendor_training_rows={report.vendor_training_eligible_rows}"
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
