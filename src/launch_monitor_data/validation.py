"""Fail-closed validation for provenance, licensing, and metric contracts."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from launch_monitor_data.contracts import METRICS
from launch_monitor_data.eligibility import load_capabilities, load_release_b_status
from launch_monitor_data.paths import (
    AGGREGATES,
    COMPARISONS,
    REFERENCES,
    SOURCE_CATALOG,
    VENDOR_FIELDS,
    require_private_authority,
)
from launch_monitor_data.units import to_canonical


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    errors: tuple[str, ...]
    source_count: int
    comparison_count: int
    vendor_field_count: int
    aggregate_count: int
    reference_value_count: int
    redistributable_count: int
    reference_only_count: int
    qualified_source_count: int = 0
    qualified_source_rows: int = 0
    strict_model_input_rows: int = 0
    capability_schema: str = ""
    release_b_planned_pairs: int = 0
    release_b_triggered_pairs: int = 0
    release_b_analyzed_pairs: int = 0
    release_b_confirmatory_ready: bool = False
    vendor_training_eligible_rows: int = 0


REFERENCE_POPULATION_TYPES = {
    "tour_average",
    "amateur_average",
    "handicap_group",
    "combine_benchmark",
    "player",
}
REFERENCE_VALUE_TYPES = {
    "group_mean",
    "season_mean",
    "session_mean",
    "single_shot",
    "max_record",
    "stock_reported",
    "benchmark",
}
REFERENCE_CONFIDENCE = {"cross_verified", "single_source", "anecdotal_rounded"}


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"Required data file is missing: {path}")
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def validate_repository_data() -> ValidationReport:
    """Validate all canonical source data without network access."""
    require_private_authority()
    capabilities = load_capabilities()
    release_b = load_release_b_status()
    errors: list[str] = []
    sources = _read_csv(SOURCE_CATALOG)
    fields = _read_csv(VENDOR_FIELDS)
    comparisons = _read_csv(COMPARISONS)
    aggregates = _read_csv(AGGREGATES) if AGGREGATES.is_file() else []
    references = _read_csv(REFERENCES) if REFERENCES.is_file() else []
    source_ids = {row["source_id"] for row in sources}
    redistributable_ids = {
        row["source_id"]
        for row in sources
        if row.get("redistribution_status") == "redistributable"
    }

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
            errors.append(
                f"vendor_fields.csv:{row_number}: "
                f"unknown source_id {row.get('source_id')}"
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

    seen_aggregates: set[tuple[str, ...]] = set()
    for row_number, row in enumerate(aggregates, start=2):
        prefix = f"aggregate_observations.csv:{row_number}"
        aggregate_key = tuple(
            row.get(column, "")
            for column in (
                "source_id",
                "monitor_vendor",
                "monitor_model",
                "cohort",
                "club",
                "metric",
            )
        )
        if aggregate_key in seen_aggregates:
            errors.append(f"{prefix}: duplicate observation key {aggregate_key}")
        seen_aggregates.add(aggregate_key)
        if row.get("source_id") not in source_ids:
            errors.append(f"{prefix}: unknown source_id {row.get('source_id')}")
        elif row.get("source_id") not in redistributable_ids:
            errors.append(
                f"{prefix}: source {row.get('source_id')} is not redistributable"
            )
        metric = row.get("metric", "")
        if metric not in METRICS:
            errors.append(f"{prefix}: unknown metric {metric}")
        else:
            try:
                to_canonical(1.0, row.get("source_unit", ""), metric)
            except ValueError:
                errors.append(
                    f"{prefix}: unit {row.get('source_unit')!r} is not "
                    f"convertible for {metric}"
                )
        for column in (
            "monitor_vendor",
            "monitor_model",
            "software_version",
            "environment",
            "cohort",
            "club",
            "measurement_status",
        ):
            if not row.get(column, "").strip():
                errors.append(f"{prefix}: missing {column}")
        if row.get("aggregation_level") != "group_mean":
            errors.append(f"{prefix}: aggregation_level must be group_mean")
        if row.get("matched_shots") not in {"0", "1"}:
            errors.append(f"{prefix}: matched_shots must be 0 or 1")
        try:
            if int(row.get("sample_count", "0")) <= 0:
                errors.append(f"{prefix}: non-positive sample_count")
            mean = float(row["reported_mean"])
            if not math.isfinite(mean):
                errors.append(f"{prefix}: reported_mean must be finite")
            if row.get("reported_sd", "").strip():
                sd = float(row["reported_sd"])
                if not math.isfinite(sd) or sd < 0:
                    errors.append(
                        f"{prefix}: reported_sd must be finite and non-negative"
                    )
        except (KeyError, ValueError):
            errors.append(f"{prefix}: invalid numeric field")

    seen_references: set[tuple[str, ...]] = set()
    for row_number, row in enumerate(references, start=2):
        prefix = f"published_references.csv:{row_number}"
        reference_key = tuple(
            row.get(column, "")
            for column in (
                "source_id",
                "population",
                "context",
                "club",
                "metric_native",
                "year",
                "value_type",
            )
        )
        if reference_key in seen_references:
            errors.append(f"{prefix}: duplicate reference key {reference_key}")
        seen_references.add(reference_key)
        if row.get("source_id") not in source_ids:
            errors.append(f"{prefix}: unknown source_id {row.get('source_id')}")
        if row.get("population_type") not in REFERENCE_POPULATION_TYPES:
            errors.append(
                f"{prefix}: invalid population_type {row.get('population_type')}"
            )
        if row.get("value_type") not in REFERENCE_VALUE_TYPES:
            errors.append(f"{prefix}: invalid value_type {row.get('value_type')}")
        if row.get("confidence") not in REFERENCE_CONFIDENCE:
            errors.append(f"{prefix}: invalid confidence {row.get('confidence')}")
        for column in ("population", "club", "metric_native", "source_unit"):
            if not row.get(column, "").strip():
                errors.append(f"{prefix}: missing {column}")
        citations = row.get("citation_urls", "")
        if not citations.strip():
            errors.append(f"{prefix}: missing citation_urls")
        elif not all(
            url.strip().startswith("http")
            for url in citations.split(";")
            if url.strip()
        ):
            errors.append(f"{prefix}: citation_urls must be URLs")
        metric = row.get("metric", "").strip()
        if metric:
            if metric not in METRICS:
                errors.append(f"{prefix}: unknown metric {metric}")
            else:
                try:
                    to_canonical(1.0, row.get("source_unit", ""), metric)
                except ValueError:
                    errors.append(
                        f"{prefix}: unit {row.get('source_unit')!r} is not "
                        f"convertible for {metric}"
                    )
        try:
            value = float(row["value"])
            if not math.isfinite(value):
                errors.append(f"{prefix}: value must be finite")
        except (KeyError, ValueError):
            errors.append(f"{prefix}: invalid value")

    return ValidationReport(
        ok=not errors,
        errors=tuple(errors),
        source_count=len(sources),
        comparison_count=len(comparisons),
        vendor_field_count=len(fields),
        aggregate_count=len(aggregates),
        reference_value_count=len(references),
        redistributable_count=sum(
            row["redistribution_status"] == "redistributable" for row in sources
        ),
        reference_only_count=sum(
            row["redistribution_status"] == "reference_only" for row in sources
        ),
        qualified_source_count=sum(
            int(vendor["source_count"]) for vendor in capabilities["vendors"]
        ),
        qualified_source_rows=int(capabilities["source_rows"]),
        strict_model_input_rows=int(capabilities["strict_model_input_rows"]),
        capability_schema=str(capabilities["schema"]),
        release_b_planned_pairs=release_b.planned_pairs,
        release_b_triggered_pairs=release_b.triggered_pairs,
        release_b_analyzed_pairs=release_b.analyzed_pairs,
        release_b_confirmatory_ready=release_b.confirmatory_ready,
        vendor_training_eligible_rows=release_b.vendor_training_eligible_rows,
    )
