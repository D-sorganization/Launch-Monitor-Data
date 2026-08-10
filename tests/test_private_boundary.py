from __future__ import annotations

import json
import os
import runpy
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_public_tree_tracks_no_live_data_artifacts() -> None:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    forbidden_suffixes = {".csv", ".db", ".jsonl", ".parquet", ".sqlite", ".xlsx"}
    tracked = [Path(line) for line in result.stdout.splitlines()]
    violations = [path for path in tracked if path.suffix.lower() in forbidden_suffixes]
    assert violations == []
    assert not (ROOT / "data").exists()
    assert not (ROOT / "database").exists()


def test_lock_pins_private_repository_to_full_commit() -> None:
    lock = json.loads((ROOT / "private_data.lock.json").read_text(encoding="utf-8"))
    assert lock["repository"].endswith(
        "D-sorganization/Launch-Monitor-Flight-Model-Campaign.git"
    )
    assert len(lock["commit"]) == 40
    assert lock["authority_path"] == "data/authority"


def test_missing_private_checkout_fails_closed(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(ROOT / "scripts" / "sync_private_data.py"))
    sync_error = namespace["SyncError"]
    with pytest.raises(sync_error, match="checkout is missing"):
        namespace["check_checkout"](tmp_path / "missing")


def test_paths_resolve_only_inside_private_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_root = ROOT / "private-test-root"
    monkeypatch.setenv("LAUNCH_MONITOR_DATA_ROOT", os.fspath(private_root))
    namespace = runpy.run_path(str(ROOT / "src" / "launch_monitor_data" / "paths.py"))
    assert namespace["DATA_DIR"] == (
        private_root.resolve() / "data" / "authority" / "catalog" / "data"
    )
    with pytest.raises(FileNotFoundError, match="sync_private_data.py sync"):
        namespace["require_private_authority"]()
