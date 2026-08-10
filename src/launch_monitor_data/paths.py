"""Authenticated private-authority data locations."""

import os
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_CHECKOUT = Path(
    os.environ.get(
        "LAUNCH_MONITOR_DATA_ROOT",
        REPOSITORY_ROOT / "private_data" / "launch-monitor-authority",
    )
).resolve()
AUTHORITY_DIR = PRIVATE_CHECKOUT / "data" / "authority"
DATA_DIR = AUTHORITY_DIR / "catalog" / "data"
SOURCE_CATALOG = DATA_DIR / "source_catalog.csv"
VENDOR_FIELDS = DATA_DIR / "vendor_fields.csv"
COMPARISONS = DATA_DIR / "studies" / "bliss_langdown_2026_comparisons.csv"
AGGREGATES = DATA_DIR / "studies" / "aggregate_observations.csv"
REFERENCES = DATA_DIR / "reference" / "published_references.csv"


def require_private_authority() -> None:
    """Require the authenticated checkout before any data operation."""
    manifest = AUTHORITY_DIR / "AUTHORITY_MANIFEST.json"
    if not manifest.is_file():
        raise FileNotFoundError(
            "private launch-monitor authority is unavailable; run "
            "`python scripts/sync_private_data.py sync` with authorized access "
            "and set LAUNCH_MONITOR_DATA_ROOT to that checkout"
        )
