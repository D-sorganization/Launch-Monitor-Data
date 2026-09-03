from __future__ import annotations

import hashlib
import json
import os
import runpy
import subprocess
from pathlib import Path

import pytest

from launch_monitor_data import paths

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
    assert not (ROOT / "results").exists()
    assert not any(path.parts[0] == "private_data" for path in tracked)


def test_lock_pins_private_repository_to_full_commit() -> None:
    lock = json.loads((ROOT / "private_data.lock.json").read_text(encoding="utf-8"))
    assert lock["repository"].endswith(
        "D-sorganization/Launch-Monitor-Flight-Model-Campaign.git"
    )
    assert len(lock["commit"]) == 40
    assert lock["commit"] == "bc44ecf051300b38dd87c745a104a0d6402faec2"
    assert paths.locked_private_commit() == lock["commit"]
    assert lock["authority_path"] == "data/authority"


def test_missing_private_checkout_fails_closed(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(ROOT / "scripts" / "sync_private_data.py"))
    sync_error = namespace["SyncError"]
    with pytest.raises(sync_error, match="checkout is missing"):
        namespace["check_checkout"](tmp_path / "missing")


def test_checkout_without_qualification_metadata_fails_closed(
    tmp_path: Path,
) -> None:
    namespace = runpy.run_path(str(ROOT / "scripts" / "sync_private_data.py"))
    checkout = tmp_path / "checkout"
    (checkout / ".git").mkdir(parents=True)
    authority = checkout / "data" / "authority"
    authority.mkdir(parents=True)
    (authority / "AUTHORITY_MANIFEST.json").write_text("{}", encoding="utf-8")
    namespace["check_checkout"].__globals__["_run"] = lambda arguments, cwd=None: (
        paths.locked_private_commit()
    )
    with pytest.raises(namespace["SyncError"], match="qualification metadata"):
        namespace["check_checkout"](checkout)


def test_checkout_without_release_b_metadata_fails_closed(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(ROOT / "scripts" / "sync_private_data.py"))
    checkout = tmp_path / "checkout"
    (checkout / ".git").mkdir(parents=True)
    authority = checkout / "data" / "authority"
    authority.mkdir(parents=True)
    (authority / "AUTHORITY_MANIFEST.json").write_text("{}", encoding="utf-8")
    output = checkout / "results" / "v2"
    output.mkdir(parents=True)
    capability = output / "capability_manifest.json"
    capability.write_text(
        json.dumps({"schema": "launch-monitor-capability-manifest/v1"}),
        encoding="utf-8",
    )
    eligibility = output / "source_metric_eligibility.csv"
    eligibility.write_text("", encoding="utf-8")
    qualification = {
        "schema": "launch-monitor-data-qualification-manifest/v1",
        "output_sha256": {
            capability.name: hashlib.sha256(capability.read_bytes()).hexdigest(),
            eligibility.name: hashlib.sha256(eligibility.read_bytes()).hexdigest(),
        },
    }
    (output / "qualification_manifest.json").write_text(
        json.dumps(qualification), encoding="utf-8"
    )
    namespace["check_checkout"].__globals__["_run"] = lambda arguments, cwd=None: (
        paths.locked_private_commit()
    )
    with pytest.raises(namespace["SyncError"], match="Release B status"):
        namespace["check_checkout"](checkout)


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


def test_package_rejects_a_mismatched_private_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checkout = tmp_path / "checkout"
    (checkout / ".git").mkdir(parents=True)
    authority = checkout / "data" / "authority"
    authority.mkdir(parents=True)
    (authority / "AUTHORITY_MANIFEST.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(paths, "private_checkout", lambda: checkout)
    monkeypatch.setattr(paths, "_git_head", lambda checkout: "0" * 40)
    with pytest.raises(ValueError, match="expected bc44ecf"):
        paths.verify_locked_private_checkout()
