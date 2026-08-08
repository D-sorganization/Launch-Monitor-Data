"""Repository data locations."""

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPOSITORY_ROOT / "data"
SOURCE_CATALOG = DATA_DIR / "source_catalog.csv"
VENDOR_FIELDS = DATA_DIR / "vendor_fields.csv"
COMPARISONS = DATA_DIR / "studies" / "bliss_langdown_2026_comparisons.csv"
AGGREGATES = DATA_DIR / "studies" / "aggregate_observations.csv"
REFERENCES = DATA_DIR / "reference" / "published_references.csv"
