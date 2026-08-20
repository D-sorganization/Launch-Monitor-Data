"""Sync the commit-pinned private launch-monitor data authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "private_data.lock.json"
DESTINATION = ROOT / "private_data" / "launch-monitor-authority"


class SyncError(RuntimeError):
    """Raised when the authenticated private checkout violates its lock."""


def _run(arguments: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        arguments,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise SyncError(f"{' '.join(arguments[:2])} failed: {detail}")
    return result.stdout.strip()


def _read_lock() -> dict[str, object]:
    lock: dict[str, object] = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    commit = lock.get("commit")
    if lock.get("schema_version") != 1:
        raise SyncError("unsupported private data lock schema")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise SyncError("private data lock must contain a full commit SHA")
    return lock


def check_checkout(destination: Path = DESTINATION) -> None:
    """Require the exact checkout and hash-verified qualified metadata."""
    lock = _read_lock()
    if not (destination / ".git").exists():
        raise SyncError(
            "private data checkout is missing; run "
            "`python scripts/sync_private_data.py sync` with authorized access"
        )
    head = _run(["git", "rev-parse", "HEAD"], cwd=destination)
    if head != lock["commit"]:
        raise SyncError(f"private checkout is {head}; expected {lock['commit']}")
    authority = destination / str(lock["authority_path"])
    if not (authority / "AUTHORITY_MANIFEST.json").is_file():
        raise SyncError(f"authority manifest is missing from {authority}")
    output = destination / "results" / "v2"
    qualification_path = output / "qualification_manifest.json"
    capability_path = output / "capability_manifest.json"
    eligibility_path = output / "source_metric_eligibility.csv"
    if not qualification_path.is_file():
        raise SyncError("private checkout lacks v2 qualification metadata")
    try:
        qualification = json.loads(qualification_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError("private qualification manifest is unreadable") from error
    if qualification.get("schema") != "launch-monitor-data-qualification-manifest/v1":
        raise SyncError("unsupported private qualification schema")
    outputs = qualification.get("output_sha256")
    if not isinstance(outputs, dict):
        raise SyncError("private qualification manifest has no output hashes")
    for name, path in (
        ("capability_manifest.json", capability_path),
        ("source_metric_eligibility.csv", eligibility_path),
    ):
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
        if actual != outputs.get(name):
            raise SyncError(f"private qualification metadata hash mismatch for {name}")
    try:
        capability = json.loads(capability_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError("private capability manifest is unreadable") from error
    if capability.get("schema") != "launch-monitor-capability-manifest/v1":
        raise SyncError("unsupported private capability schema")
    release_b = destination / "results" / "release_b"
    release_status_path = release_b / "status.json"
    try:
        release_status = json.loads(release_status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError("private Release B status is missing or unreadable") from error
    if release_status.get("schema") != "release-b-collection-status/v1":
        raise SyncError("unsupported private Release B status schema")
    for key, path in (
        ("schedule_sha256", release_b / "confirmatory_schedule.csv"),
        ("ledger_sha256", release_b / "collection_ledger.csv"),
    ):
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
        if actual != release_status.get(key):
            raise SyncError(f"private Release B metadata hash mismatch for {path.name}")


def sync_checkout(destination: Path = DESTINATION) -> None:
    """Clone or update only to the immutable commit in the lock file."""
    lock = _read_lock()
    repository = str(lock["repository"])
    commit = str(lock["commit"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not (destination / ".git").exists():
        _run(["git", "clone", "--no-checkout", repository, str(destination)])
    remote = _run(["git", "remote", "get-url", "origin"], cwd=destination)
    if remote.rstrip("/") != repository.rstrip("/"):
        raise SyncError(f"private checkout origin is {remote}; expected {repository}")
    _run(["git", "fetch", "--depth", "1", "origin", commit], cwd=destination)
    _run(["git", "checkout", "--detach", "--force", commit], cwd=destination)
    check_checkout(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("sync", "check"))
    args = parser.parse_args()
    try:
        if args.command == "sync":
            sync_checkout()
        else:
            check_checkout()
    except SyncError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(f"private launch-monitor authority verified at {DESTINATION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
