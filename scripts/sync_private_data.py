"""Sync the commit-pinned private launch-monitor data authority."""

from __future__ import annotations

import argparse
import json
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
    if not isinstance(commit, str) or len(commit) != 40:
        raise SyncError("private data lock must contain a full commit SHA")
    return lock


def check_checkout(destination: Path = DESTINATION) -> None:
    """Require an exact locked checkout with an authority manifest."""
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
