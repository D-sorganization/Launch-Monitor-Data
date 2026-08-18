"""Deterministic bidirectional unit conversion for canonical metrics."""

from __future__ import annotations

import math

from launch_monitor_data.contracts import METRICS

# Factor from each supported source unit into its canonical SI unit.
CONVERSION_FACTORS: dict[tuple[str, str], float] = {
    ("m/s", "m/s"): 1.0,
    ("mph", "m/s"): 0.44704,
    ("km/h", "m/s"): 1.0 / 3.6,
    ("m", "m"): 1.0,
    ("yd", "m"): 0.9144,
    ("ft", "m"): 0.3048,
    ("in", "m"): 0.0254,
    ("mm", "m"): 0.001,
    ("deg", "rad"): math.pi / 180.0,
    ("rad", "rad"): 1.0,
    ("rpm", "rad/s"): 2.0 * math.pi / 60.0,
    ("rad/s", "rad/s"): 1.0,
    ("s", "s"): 1.0,
    ("1", "1"): 1.0,
}


def conversion_factor(source_unit: str, metric: str) -> float:
    """Return the multiplier converting ``source_unit`` to canonical."""
    if metric not in METRICS:
        raise ValueError(f"Unknown canonical metric: {metric}")
    canonical_unit = METRICS[metric].canonical_unit
    unit = source_unit.strip().lower()
    try:
        return CONVERSION_FACTORS[(unit, canonical_unit)]
    except KeyError as exc:
        raise ValueError(
            f"Cannot convert {source_unit!r} to {canonical_unit!r} for {metric}"
        ) from exc


def to_canonical(value: float, source_unit: str, metric: str) -> tuple[float, str]:
    """Convert one reported value to the canonical unit."""
    return (
        value * conversion_factor(source_unit, metric),
        METRICS[metric].canonical_unit,
    )


def from_canonical(value: float, target_unit: str, metric: str) -> tuple[float, str]:
    """Convert one canonical value back into ``target_unit``."""
    return value / conversion_factor(target_unit, metric), target_unit


def to_display(value: float, metric: str) -> tuple[float, str]:
    """Convert one canonical value into the metric's display unit."""
    display_unit = METRICS[metric].display_unit or METRICS[metric].canonical_unit
    return from_canonical(value, display_unit, metric)
