from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

import pytest

from launch_monitor_data.build import build_database


def test_build_exports_published_references(tmp_path: Path) -> None:
    result = build_database(output_dir=tmp_path)

    assert result.reference_value_count >= 500

    with (tmp_path / "published_references.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))

    assert len(rows) == result.reference_value_count
    assert all(row["citation_urls"] for row in rows)
    assert {row["population_type"] for row in rows} >= {
        "tour_average",
        "amateur_average",
        "player",
    }

    pga_driver_carry = next(
        row
        for row in rows
        if row["population"] == "pga_tour"
        and row["context"] == "classic_data_sheet"
        and row["club"] == "Driver"
        and row["metric_native"] == "carry"
    )
    assert float(pga_driver_carry["value"]) == 275.0
    assert float(pga_driver_carry["canonical_value"]) == pytest.approx(
        275 * 0.9144
    )
    assert pga_driver_carry["canonical_unit"] == "m"


def test_published_references_join_to_sources(tmp_path: Path) -> None:
    build_database(output_dir=tmp_path)

    with sqlite3.connect(tmp_path / "launch_monitor_data.sqlite") as connection:
        missing = connection.execute(
            """
            SELECT COUNT(*)
            FROM published_references AS reference
            LEFT JOIN sources AS source USING (source_id)
            WHERE source.source_id IS NULL
            """
        ).fetchone()
        distinct_ids = connection.execute(
            "SELECT COUNT(DISTINCT reference_id), COUNT(*) "
            "FROM published_references"
        ).fetchone()
    assert missing == (0,)
    assert distinct_ids[0] == distinct_ids[1]
