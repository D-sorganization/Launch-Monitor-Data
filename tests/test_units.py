from __future__ import annotations

import math

import pytest

from launch_monitor_data.units import to_canonical


@pytest.mark.parametrize(
    ("value", "unit", "metric", "expected"),
    [
        (100.0, "mph", "ball_speed", 44.704),
        (100.0, "yd", "carry_distance", 91.44),
        (100.0, "ft", "apex_height", 30.48),
        (60.0, "rpm", "spin_rate", 2 * math.pi),
        (180.0, "deg", "launch_angle", math.pi),
        (1.42, "1", "smash_factor", 1.42),
    ],
)
def test_to_canonical(value: float, unit: str, metric: str, expected: float) -> None:
    converted, canonical_unit = to_canonical(value, unit, metric)
    assert converted == pytest.approx(expected)
    assert canonical_unit in {"m/s", "m", "rad/s", "rad", "1"}


def test_to_canonical_rejects_unknown_metric() -> None:
    with pytest.raises(ValueError, match="Unknown canonical metric"):
        to_canonical(1.0, "mph", "invented_metric")
