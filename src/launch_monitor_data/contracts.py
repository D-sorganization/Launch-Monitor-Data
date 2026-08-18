"""Canonical metric contract shared across the launch-monitor ecosystem.

This is the single source of truth for canonical shot-metric names, categories,
and units, kept in name-and-unit parity with UpstreamDrift's
``src/shared/python/launch_monitor/schema.py`` so canonical frames flow between
the repositories without renaming. Canonical units are SI: angles in radians,
speeds in metres per second, distances in metres, spin in radians per second,
time in seconds.
"""

from __future__ import annotations

from dataclasses import dataclass

CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True)
class MetricContract:
    name: str
    category: str
    canonical_unit: str
    label: str = ""
    display_unit: str = ""
    derived_from: tuple[str, ...] = ()


def _metric(
    name: str,
    category: str,
    canonical_unit: str,
    label: str,
    display_unit: str,
    derived_from: tuple[str, ...] = (),
) -> MetricContract:
    return MetricContract(
        name, category, canonical_unit, label, display_unit, derived_from
    )


METRICS = {
    item.name: item
    for item in (
        _metric("club_speed", "club", "m/s", "Club Speed", "mph"),
        _metric("attack_angle", "club", "rad", "Attack Angle", "deg"),
        _metric("club_path", "club", "rad", "Club Path", "deg"),
        _metric("face_angle", "club", "rad", "Face Angle", "deg"),
        _metric(
            "face_to_path",
            "club",
            "rad",
            "Face to Path",
            "deg",
            ("face_angle", "club_path"),
        ),
        _metric("dynamic_loft", "club", "rad", "Dynamic Loft", "deg"),
        _metric("dynamic_lie", "club", "rad", "Dynamic Lie", "deg"),
        _metric("spin_loft", "club", "rad", "Spin Loft", "deg"),
        _metric("swing_direction", "club", "rad", "Swing Direction", "deg"),
        _metric("swing_plane", "club", "rad", "Swing Plane", "deg"),
        _metric("low_point_distance", "club", "m", "Low Point", "in"),
        _metric("impact_height", "club", "m", "Impact Height", "mm"),
        _metric("impact_offset", "club", "m", "Impact Offset", "mm"),
        _metric("ball_speed", "launch", "m/s", "Ball Speed", "mph"),
        _metric("launch_angle", "launch", "rad", "Launch Angle", "deg"),
        _metric("launch_direction", "launch", "rad", "Launch Direction", "deg"),
        _metric("spin_rate", "launch", "rad/s", "Spin Rate", "rpm"),
        _metric("back_spin", "launch", "rad/s", "Back Spin", "rpm"),
        _metric("side_spin", "launch", "rad/s", "Side Spin", "rpm"),
        _metric("spin_axis", "launch", "rad", "Spin Axis", "deg"),
        _metric(
            "smash_factor",
            "launch",
            "1",
            "Smash Factor",
            "1",
            ("ball_speed", "club_speed"),
        ),
        _metric("carry_distance", "flight", "m", "Carry Distance", "yd"),
        _metric("total_distance", "flight", "m", "Total Distance", "yd"),
        _metric("roll_distance", "flight", "m", "Roll Distance", "yd"),
        _metric("lateral_carry", "flight", "m", "Lateral Carry", "yd"),
        _metric("lateral_total", "flight", "m", "Lateral Total", "yd"),
        _metric("apex_height", "flight", "m", "Apex Height", "ft"),
        _metric("flight_time", "flight", "s", "Flight Time", "s"),
        _metric("descent_angle", "flight", "rad", "Descent Angle", "deg"),
        _metric("curve", "flight", "m", "Curve", "yd"),
        _metric("putt_distance", "putting", "m", "Putt Distance", "ft"),
        _metric("skid_distance", "putting", "m", "Skid Distance", "in"),
        _metric("roll_speed", "putting", "m/s", "Roll Speed", "mph"),
    )
}
