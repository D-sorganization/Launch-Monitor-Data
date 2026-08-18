from __future__ import annotations

import math

import pytest

from launch_monitor_data.contracts import CONTRACT_VERSION, METRICS
from launch_monitor_data.units import (
    from_canonical,
    to_canonical,
    to_display,
)


def test_contract_shape_and_version() -> None:
    assert CONTRACT_VERSION == "1.0.0"
    assert len(METRICS) == 33
    assert {metric.category for metric in METRICS.values()} == {
        "club",
        "launch",
        "flight",
        "putting",
    }
    assert {metric.canonical_unit for metric in METRICS.values()} == {
        "m/s",
        "rad",
        "rad/s",
        "m",
        "s",
        "1",
    }
    for metric in METRICS.values():
        assert metric.label
        assert metric.display_unit


def test_derived_metrics_reference_known_parents() -> None:
    for metric in METRICS.values():
        for parent in metric.derived_from:
            assert parent in METRICS


@pytest.mark.parametrize(
    ("value", "unit", "metric", "expected"),
    [
        (100.0, "mph", "ball_speed", 44.704),
        (10.0, "deg", "launch_angle", math.pi / 18.0),
        (3000.0, "rpm", "spin_rate", 3000.0 * math.pi / 30.0),
        (250.0, "yd", "carry_distance", 228.6),
        (90.0, "ft", "apex_height", 27.432),
        (1.48, "1", "smash_factor", 1.48),
    ],
)
def test_to_canonical_conversions(
    value: float, unit: str, metric: str, expected: float
) -> None:
    converted, canonical_unit = to_canonical(value, unit, metric)
    assert converted == pytest.approx(expected)
    assert canonical_unit == METRICS[metric].canonical_unit


@pytest.mark.parametrize(
    ("unit", "metric"),
    [("mph", "ball_speed"), ("deg", "face_angle"), ("rpm", "back_spin")],
)
def test_round_trip_is_identity(unit: str, metric: str) -> None:
    canonical, _ = to_canonical(123.4, unit, metric)
    recovered, recovered_unit = from_canonical(canonical, unit, metric)
    assert recovered == pytest.approx(123.4)
    assert recovered_unit == unit


def test_to_display_uses_contract_display_unit() -> None:
    value, unit = to_display(44.704, "ball_speed")
    assert value == pytest.approx(100.0)
    assert unit == "mph"


def test_unknown_metric_and_unit_fail_closed() -> None:
    with pytest.raises(ValueError, match="Unknown canonical metric"):
        to_canonical(1.0, "mph", "warp_speed")
    with pytest.raises(ValueError, match="Cannot convert"):
        to_canonical(1.0, "furlongs", "carry_distance")
