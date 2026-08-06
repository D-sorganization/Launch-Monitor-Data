"""Fail-closed validation for provenance, licensing, and metric contracts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from launch_monitor_data.contracts import METRICS
from launch_monitor_data.paths import COMPARISONS, SOURCE_CATALOG, VENDOR_FIELDS


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    errors: tuple[str, ...]
    source_count: int
    comparison_count: int
    vendor_field_count: int
    redistributable_count: int
    reference_only_count: int


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"Required data file is missing: {path}")
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def validate_repository_data() -> ValidationReport:
    """Validate all canonical source data without network access."""
    errors: list[str] = []
    sources = _read_csv(SOURCE_CATALOG)
    fields = _read_csv(VENDOR_FIELDS)
    comparisons = _read_csv(COMPARISONS)
    source_ids = {row["source_id"] for row in sources}

    if len(source_ids) != len(sources):
        errors.append("source_id values must be unique")
    for row_number, row in enumerate(sources, start=2):
        source_id = row.get("source_id", "").strip()
        if not source_id:
            errors.append(f"source_catalog.csv:{row_number}: missing source_id")
        if not row.get("url", "").startswith("https://"):
            errors.append(f"{source_id}: source URL must use https")
        status = row.get("redistribution_status")
        if status not in {"redistributable", "reference_only"}:
            errors.append(f"{source_id}: invalid redistribution_status")
        if status == "redistributable" and not row.get("license_spdx"):
            errors.append(f"{source_id}: redistributable source lacks a license")

    for row_number, row in enumerate(fields, start=2):
        if row.get("source_id") not in source_ids:
            source_id = row.get("source_id")
            errors.append(
                f"vendor_fields.csv:{row_number}: unknown source_id {source_id}"
            )
        if row.get("metric") not in METRICS:
            errors.append(
                f"vendor_fields.csv:{row_number}: unknown metric {row.get('metric')}"
            )

    seen_comparisons: set[tuple[str, str]] = set()
    for row_number, row in enumerate(comparisons, start=2):
        key = (row.get("club", ""), row.get("metric", ""))
        if key in seen_comparisons:
            errors.append(f"comparisons:{row_number}: duplicate club/metric {key}")
        seen_comparisons.add(key)
        if row.get("source_id") not in source_ids:
            errors.append(f"comparisons:{row_number}: unknown source_id")
        if row.get("metric") not in METRICS:
            errors.append(f"comparisons:{row_number}: unknown metric")
        if row.get("source_unit") not in {"mph", "yd", "ft", "deg", "rpm", "1"}:
            errors.append(f"comparisons:{row_number}: unsupported source unit")
        try:
            if int(row.get("sample_count", "0")) <= 0:
                errors.append(f"comparisons:{row_number}: non-positive sample_count")
            for column in (
                "trackman_mean",
                "trackman_sd",
                "flightscope_mean",
                "flightscope_sd",
            ):
                float(row[column])
        except (KeyError, ValueError):
            errors.append(f"comparisons:{row_number}: invalid numeric field")

    return ValidationReport(
        ok=not errors,
        errors=tuple(errors),
        source_count=len(sources),
        comparison_count=len(comparisons),
        vendor_field_count=len(fields),
        redistributable_count=sum(
            row["redistribution_status"] == "redistributable" for row in sources
        ),
        reference_only_count=sum(
            row["redistribution_status"] == "reference_only" for row in sources
        ),
    )
