"""Authenticated private-authority data locations."""

import os
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


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
