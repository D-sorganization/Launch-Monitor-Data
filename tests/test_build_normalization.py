"""Data-free tests of the catalog build's pure normalization functions."""

from __future__ import annotations

import math

from launch_monitor_data.build import (
    _normalize_aggregates,
    _normalize_observations,
    _normalize_references,
    _observation_id,
)


def test_observation_id_is_deterministic_and_cohort_sensitive() -> None:
    base = _observation_id("src", "Driver", "ball_speed", "TrackMan")
    assert base == _observation_id("src", "Driver", "ball_speed", "TrackMan")
    assert len(base) == 24
    cohort = _observation_id(
        "src", "Driver", "ball_speed", "TrackMan", cohort="tour", model="4"
    )
    assert cohort != base


def test_normalize_observations_emits_both_monitors_in_canonical_units() -> None:
    comparisons = [
        {
            "source_id": "study",
            "club": "Driver",
            "metric": "ball_speed",
            "source_unit": "mph",
            "sample_count": "10",
            "measurement_status": "reported",
            "software_version": "v1",
            "environment": "indoor",
            "trackman_mean": "150.0",
            "trackman_sd": "2.0",
            "flightscope_mean": "149.0",
            "flightscope_sd": "2.5",
        }
    ]
    rows = _normalize_observations(comparisons)
    assert [row["monitor_vendor"] for row in rows] == ["TrackMan", "FlightScope"]
    trackman = rows[0]
    assert trackman["canonical_mean"] == 150.0 * 0.44704
    assert trackman["canonical_unit"] == "m/s"
    assert trackman["aggregation_level"] == "group_mean"


def test_normalize_aggregates_allows_missing_sd() -> None:
    aggregates = [
        {
            "source_id": "tour",
            "monitor_vendor": "TrackMan",
            "monitor_model": "4",
            "software_version": "",
            "environment": "outdoor",
            "cohort": "pga_tour",
            "club": "Driver",
            "metric": "launch_angle",
            "aggregation_level": "group_mean",
            "sample_count": "500",
            "measurement_status": "reported",
            "reported_mean": "10.9",
            "reported_sd": "",
            "source_unit": "deg",
            "matched_shots": "0",
        }
    ]
    rows = _normalize_aggregates(aggregates)
    assert rows[0]["reported_sd"] is None
    assert rows[0]["canonical_sd"] is None
    assert rows[0]["canonical_mean"] == 10.9 * math.pi / 180.0


def test_normalize_references_converts_only_mapped_metrics() -> None:
    references = [
        {
            "source_id": "ref",
            "population_type": "tour",
            "population": "PGA Tour",
            "context": "season average",
            "monitor": "ShotLink",
            "year": "2025",
            "club": "Driver",
            "metric_native": "Driving Distance",
            "metric": "carry_distance",
            "value": "282.0",
            "source_unit": "yd",
            "value_type": "mean",
            "confidence": "high",
            "citation_urls": "https://example.test",
            "notes": "",
        },
        {
            "source_id": "ref",
            "population_type": "tour",
            "population": "PGA Tour",
            "context": "season average",
            "monitor": "ShotLink",
            "year": "2025",
            "club": "Driver",
            "metric_native": "Unmapped Native Stat",
            "metric": "",
            "value": "1.0",
            "source_unit": "1",
            "value_type": "mean",
            "confidence": "low",
            "citation_urls": "https://example.test",
            "notes": "",
        },
    ]
    rows = _normalize_references(references)
    assert rows[0]["canonical_value"] == 282.0 * 0.9144
    assert rows[0]["canonical_unit"] == "m"
    assert rows[1]["canonical_value"] is None
    assert rows[0]["reference_id"] != rows[1]["reference_id"]
