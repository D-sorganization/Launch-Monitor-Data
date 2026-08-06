"""Deterministic source-to-canonical unit conversion."""

from __future__ import annotations

import math

from launch_monitor_data.contracts import METRICS


def to_canonical(value: float, source_unit: str, metric: str) -> tuple[float, str]:
    """Convert one reported value to the UpstreamDrift canonical unit."""
    if metric not in METRICS:
        raise ValueError(f"Unknown canonical metric: {metric}")
    canonical_unit = METRICS[metric].canonical_unit
    unit = source_unit.strip().lower()
    factors: dict[tuple[str, str], float] = {
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
    try:
        factor = factors[(unit, canonical_unit)]
    except KeyError as exc:
        raise ValueError(
            f"Cannot convert {source_unit!r} to {canonical_unit!r} for {metric}"
        ) from exc
    return value * factor, canonical_unit
