"""Corpus-reader tests over synthetic, test-generated Parquet fixtures.

No real shot data enters the public tree: every fixture is built in tmp_path
at test time, honoring the private-boundary contract.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

pa = pytest.importorskip("pyarrow")
import pyarrow.parquet as pq  # noqa: E402

from launch_monitor_data import corpus  # noqa: E402

SYNTHETIC_ROWS = {
    "synthetic_trackman": {
        "monitor": ["TrackMan"],
        "file": ["a.csv"],
        "row_index": [0],
        "club": ["Driver"],
        "club_speed_mph": [100.0],
        "ball_speed_mph": [150.0],
        "smash_factor": [1.5],
        "launch_angle_deg": [12.0],
        "launch_direction_deg": [1.0],
        "spin_rate_rpm": [2700.0],
        "back_spin_rpm": [2600.0],
        "side_spin_rpm": [300.0],
        "spin_axis_deg": [4.0],
        "attack_angle_deg": [-1.2],
        "club_path_deg": [0.5],
        "face_angle_deg": [0.2],
        "carry_yd": [250.0],
        "total_yd": [270.0],
        "apex_native": [95.0],
        "descent_angle_deg": [38.0],
        "native_json": [json.dumps({"Club Speed": "100.0"})],
    },
    "synthetic_mevo": {
        "monitor": ["FlightScope Mevo+"],
        "file": ["b.csv"],
        "row_index": [0],
        "club": ["7 Iron"],
        "club_speed_mph": [80.0],
        "ball_speed_mph": [110.0],
        "smash_factor": [1.375],
        "launch_angle_deg": [18.0],
        "launch_direction_deg": [-0.5],
        "spin_rate_rpm": [6500.0],
        "back_spin_rpm": [6400.0],
        "side_spin_rpm": [-200.0],
        "spin_axis_deg": [-2.0],
        "attack_angle_deg": [-4.0],
        "club_path_deg": [1.5],
        "face_angle_deg": [0.8],
        "carry_yd": [165.0],
        "total_yd": [172.0],
        "apex_native": [28.0],
        "descent_angle_deg": [45.0],
        "native_json": [json.dumps({"Ball Speed": "110.0"})],
    },
}


@pytest.fixture()
def synthetic_authority(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    authority = tmp_path / "checkout" / "data" / "authority"
    dataset_dir = authority / "database" / "shot_corpus_parquet"
    for source_id, rows in SYNTHETIC_ROWS.items():
        partition = dataset_dir / f"source_id={source_id}"
        partition.mkdir(parents=True)
        pq.write_table(pa.table(rows), partition / "part-0.parquet")
    (authority / "AUTHORITY_MANIFEST.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("LAUNCH_MONITOR_DATA_ROOT", str(tmp_path / "checkout"))
    return authority


def test_load_shots_converts_to_canonical_units(synthetic_authority: Path) -> None:
    frame = corpus.load_shots(sources=["synthetic_trackman"])
    assert len(frame) == 1
    row = frame.iloc[0]
    assert row["ball_speed"] == pytest.approx(150.0 * 0.44704)
    assert row["club_speed"] == pytest.approx(100.0 * 0.44704)
    assert row["launch_angle"] == pytest.approx(math.radians(12.0))
    assert row["spin_rate"] == pytest.approx(2700.0 * math.pi / 30.0)
    assert row["carry_distance"] == pytest.approx(250.0 * 0.9144)
    assert row["smash_factor"] == pytest.approx(1.5)
    assert row["apex_native"] == pytest.approx(95.0)  # passthrough, unconverted
    assert row["observation_kind"] == "shot"
    assert row["monitor"] == "TrackMan"
    assert "native_json" not in frame.columns


def test_load_shots_native_units_and_all_sources(synthetic_authority: Path) -> None:
    frame = corpus.load_shots(canonical_units=False, include_native_json=True)
    assert len(frame) == 2
    assert set(frame["source_id"].astype(str)) == set(SYNTHETIC_ROWS)
    assert frame.set_index("source_id").loc["synthetic_mevo", "carry_yd"] == 165.0
    assert "ball_speed_mph" in frame.columns
    assert "native_json" in frame.columns


def test_load_shots_metric_pruning(synthetic_authority: Path) -> None:
    frame = corpus.load_shots(metrics=["ball_speed", "carry_distance"])
    assert "ball_speed" in frame.columns
    assert "carry_distance" in frame.columns
    assert "spin_rate" not in frame.columns
    assert "club" in frame.columns  # identity columns always present


def test_available_sources_lists_partitions(synthetic_authority: Path) -> None:
    assert corpus.available_sources() == sorted(SYNTHETIC_ROWS)


def test_unknown_source_and_metric_fail_closed(synthetic_authority: Path) -> None:
    with pytest.raises(ValueError, match="Unknown corpus sources"):
        corpus.load_shots(sources=["nope"])
    with pytest.raises(ValueError, match="Unknown corpus metrics"):
        corpus.load_shots(metrics=["warp_speed"])


def test_missing_authority_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LAUNCH_MONITOR_DATA_ROOT", str(tmp_path / "absent"))
    with pytest.raises(FileNotFoundError, match="sync_private_data.py sync"):
        corpus.load_shots()


def test_missing_corpus_dataset_names_the_lock_remedy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authority = tmp_path / "checkout" / "data" / "authority"
    authority.mkdir(parents=True)
    (authority / "AUTHORITY_MANIFEST.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("LAUNCH_MONITOR_DATA_ROOT", str(tmp_path / "checkout"))
    with pytest.raises(FileNotFoundError, match="private_data.lock.json"):
        corpus.load_shots()


def test_new_columns_map_to_canonical_metrics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """lateral_carry, flight_time and captured_at reach the canonical frame."""
    root = tmp_path / "checkout"
    dataset = root / "data" / "authority" / "database" / "shot_corpus_parquet"
    rows = dict(SYNTHETIC_ROWS["synthetic_trackman"])
    rows["lateral_carry_yd"] = [-12.5]
    rows["flight_time_s"] = [6.2]
    rows["captured_at"] = ["2023-08-07T00:00:00"]
    partition = dataset / "source_id=synthetic_new_columns"
    partition.mkdir(parents=True)
    pq.write_table(pa.table(rows), partition / "part-0.parquet")
    (root / "data" / "authority" / "AUTHORITY_MANIFEST.json").write_text(
        "{}", encoding="utf-8"
    )
    monkeypatch.setenv("LAUNCH_MONITOR_DATA_ROOT", str(root))

    frame = corpus.load_shots()

    row = frame.iloc[0]
    assert row["lateral_carry"] == pytest.approx(-12.5 * 0.9144)  # yards -> m
    assert row["flight_time"] == pytest.approx(6.2)  # already seconds
    assert row["captured_at"] == "2023-08-07T00:00:00"


def test_corpus_without_new_columns_still_loads(synthetic_authority: Path) -> None:
    """A corpus pinned before #18/#19 lacks the columns; loading must not fail."""
    frame = corpus.load_shots(sources=["synthetic_trackman"])

    assert len(frame) == 1
    assert "lateral_carry" not in frame.columns
    assert "captured_at" not in frame.columns
    assert frame.iloc[0]["ball_speed"] == pytest.approx(150.0 * 0.44704)
