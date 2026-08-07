from __future__ import annotations

import math

import pytest

from launch_monitor_data.build import _normalize_aggregates, _observation_id


def _row(**overrides: str) -> dict[str, str]:
    row = {
        "source_id": "example_source",
        "monitor_vendor": "TrackMan",
        "monitor_model": "TrackMan 4",
        "software_version": "unspecified",
        "environment": "outdoor_range",
        "cohort": "professional",
        "club": "Driver",
        "metric": "club_speed",
        "source_unit": "mph",
        "aggregation_level": "group_mean",
        "sample_count": "42",
        "measurement_status": "reported",
        "reported_mean": "110.0",
        "reported_sd": "3.5",
        "matched_shots": "0",
    }
    row.update(overrides)
    return row


def test_normalize_aggregates_converts_to_canonical_units() -> None:
    rows = _normalize_aggregates([_row()])

    assert len(rows) == 1
    observation = rows[0]
    assert observation["canonical_unit"] == "m/s"
    assert observation["canonical_mean"] == pytest.approx(110.0 * 0.44704)
    assert observation["canonical_sd"] == pytest.approx(3.5 * 0.44704)
    assert observation["cohort"] == "professional"
    assert observation["matched_shots"] == 0


def test_normalize_aggregates_allows_missing_sd() -> None:
    rows = _normalize_aggregates([_row(reported_sd="")])

    assert rows[0]["reported_sd"] is None
    assert rows[0]["canonical_sd"] is None
    assert math.isfinite(float(rows[0]["canonical_mean"]))


def test_observation_ids_distinguish_cohort_and_model() -> None:
    base = _observation_id("s", "Driver", "club_speed", "TrackMan")
    with_cohort = _observation_id(
        "s", "Driver", "club_speed", "TrackMan", cohort="professional"
    )
    other_model = _observation_id(
        "s",
        "Driver",
        "club_speed",
        "TrackMan",
        cohort="professional",
        model="TrackMan iO",
    )
    assert len({base, with_cohort, other_model}) == 3
