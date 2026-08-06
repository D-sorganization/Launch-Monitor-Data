"""Canonical metric contract shared with UpstreamDrift launch-monitor analytics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricContract:
    name: str
    category: str
    canonical_unit: str


METRICS = {
    item.name: item
    for item in (
        MetricContract("club_speed", "club", "m/s"),
        MetricContract("attack_angle", "club", "rad"),
        MetricContract("club_path", "club", "rad"),
        MetricContract("face_angle", "club", "rad"),
        MetricContract("face_to_path", "club", "rad"),
        MetricContract("dynamic_loft", "club", "rad"),
        MetricContract("dynamic_lie", "club", "rad"),
        MetricContract("spin_loft", "club", "rad"),
        MetricContract("swing_direction", "club", "rad"),
        MetricContract("swing_plane", "club", "rad"),
        MetricContract("low_point_distance", "club", "m"),
        MetricContract("impact_height", "club", "m"),
        MetricContract("impact_offset", "club", "m"),
        MetricContract("ball_speed", "launch", "m/s"),
        MetricContract("launch_angle", "launch", "rad"),
        MetricContract("launch_direction", "launch", "rad"),
        MetricContract("spin_rate", "launch", "rad/s"),
        MetricContract("back_spin", "launch", "rad/s"),
        MetricContract("side_spin", "launch", "rad/s"),
        MetricContract("spin_axis", "launch", "rad"),
        MetricContract("smash_factor", "launch", "1"),
        MetricContract("carry_distance", "flight", "m"),
        MetricContract("total_distance", "flight", "m"),
        MetricContract("roll_distance", "flight", "m"),
        MetricContract("lateral_carry", "flight", "m"),
        MetricContract("lateral_total", "flight", "m"),
        MetricContract("apex_height", "flight", "m"),
        MetricContract("flight_time", "flight", "s"),
        MetricContract("descent_angle", "flight", "rad"),
        MetricContract("curve", "flight", "m"),
    )
}
