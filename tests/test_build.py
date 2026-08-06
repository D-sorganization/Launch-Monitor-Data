from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from launch_monitor_data.build import build_database


def test_build_creates_traceable_normalized_database(tmp_path: Path) -> None:
    result = build_database(output_dir=tmp_path)

    assert result.source_count >= 10
    assert result.comparison_count == 57
    assert result.observation_count == 114
    assert result.vendor_count >= 6

    database = tmp_path / "launch_monitor_data.sqlite"
    assert database.is_file()
    with sqlite3.connect(database) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM metric_observations"
        ).fetchone()
        missing_sources = connection.execute(
            """
            SELECT COUNT(*)
            FROM metric_observations AS observation
            LEFT JOIN sources AS source USING (source_id)
            WHERE source.source_id IS NULL
            """
        ).fetchone()
    assert count == (114,)
    assert missing_sources == (0,)


def test_build_exports_upstreamdrift_metric_vocabulary(tmp_path: Path) -> None:
    build_database(output_dir=tmp_path)

    with (tmp_path / "upstreamdrift_aggregate_metrics.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))

    assert len(rows) == 114
    assert {row["monitor_vendor"] for row in rows} == {"TrackMan", "FlightScope"}
    assert {row["aggregation_level"] for row in rows} == {"group_mean"}
    assert "ball_speed" in {row["metric"] for row in rows}
    assert all(row["source_id"] for row in rows)
    assert all(row["canonical_unit"] for row in rows)
