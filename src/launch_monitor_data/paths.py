"""Authenticated private-authority data locations."""

import json
import os
import re
import subprocess
from importlib.resources import files
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def locked_private_commit() -> str:
    """Read the canonical lock in source trees or its wheel-bundled copy."""
    source_lock = REPOSITORY_ROOT / "private_data.lock.json"
    if source_lock.is_file():
        payload = json.loads(source_lock.read_text(encoding="utf-8"))
    else:
        payload = json.loads(
            files("launch_monitor_data")
            .joinpath("private_data.lock.json")
            .read_text(encoding="utf-8")
        )
    commit = payload.get("commit")
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("private data lock must contain a full commit SHA")
    return commit


def private_checkout() -> Path:
    """Resolve the private authority checkout root at call time.

    Reads ``LAUNCH_MONITOR_DATA_ROOT`` on every call so tests and multi-root
    tooling can repoint the authority without re-importing this module.
    """
    return Path(
        os.environ.get(
            "LAUNCH_MONITOR_DATA_ROOT",
            os.fspath(REPOSITORY_ROOT / "private_data" / "launch-monitor-authority"),
        )
    ).resolve()


def authority_dir() -> Path:
    return private_checkout() / "data" / "authority"


def _git_head(checkout: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=checkout,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        raise ValueError("private launch-monitor checkout has no readable Git HEAD")
    return result.stdout.strip()


def verify_locked_private_checkout() -> Path:
    """Return the private checkout only when it is the exact Release A commit."""
    checkout = private_checkout()
    if not (checkout / ".git").exists():
        raise FileNotFoundError(
            "private launch-monitor checkout is unavailable; run "
            "`python scripts/sync_private_data.py sync` with authorized access"
        )
    actual = _git_head(checkout)
    expected = locked_private_commit()
    if actual != expected:
        raise ValueError(
            f"private checkout is {actual}; expected {expected}; "
            "run `python scripts/sync_private_data.py sync`"
        )
    require_private_authority(checkout / "data" / "authority")
    return checkout


# Import-time constants, kept for existing callers; prefer the functions above
# in new code so the environment override stays live.
PRIVATE_CHECKOUT = private_checkout()
AUTHORITY_DIR = PRIVATE_CHECKOUT / "data" / "authority"
DATA_DIR = AUTHORITY_DIR / "catalog" / "data"
SOURCE_CATALOG = DATA_DIR / "source_catalog.csv"
VENDOR_FIELDS = DATA_DIR / "vendor_fields.csv"
COMPARISONS = DATA_DIR / "studies" / "bliss_langdown_2026_comparisons.csv"
AGGREGATES = DATA_DIR / "studies" / "aggregate_observations.csv"
REFERENCES = DATA_DIR / "reference" / "published_references.csv"


def require_private_authority(root: Path | None = None) -> Path:
    """Require the authenticated checkout before any data operation."""
    authority = root if root is not None else authority_dir()
    manifest = authority / "AUTHORITY_MANIFEST.json"
    if not manifest.is_file():
        raise FileNotFoundError(
            "private launch-monitor authority is unavailable; run "
            "`python scripts/sync_private_data.py sync` with authorized access "
            "and set LAUNCH_MONITOR_DATA_ROOT to that checkout"
        )
    return authority
