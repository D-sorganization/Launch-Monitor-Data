"""Keep docs/SCHEMA.md in lockstep with the real schema contracts.

The schema documentation is a contract surface: contributors (human and
agent) read it to write queries and parsers, so it must not drift from the
code that actually creates the tables and reads the shot corpus. These tests
fail whenever the shipped schema or the documented schema changes without
the other following, per the specification-driven review gates.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from launch_monitor_data.build import _create_database
from launch_monitor_data.corpus import (
    CORPUS_COLUMN_MAP,
    IDENTITY_COLUMNS,
    PASSTHROUGH_COLUMNS,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DOC = ROOT / "docs" / "SCHEMA.md"


def _build_tables(tmp_path: Path) -> dict[str, list[str]]:
    """Introspect the schema that build.py actually creates."""
    db_path = tmp_path / "schema.sqlite"
    _create_database(db_path, [], [], [], [], [])
    # _create_database's sqlite connection context manager commits but does
    # not close on all platforms; collect it so Windows can remove the file.
    import gc

    gc.collect()
    connection = sqlite3.connect(db_path)
    try:
        tables = {
            name: [row[1] for row in connection.execute(f"PRAGMA table_info({name})")]
            for (name,) in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        }
    finally:
        connection.close()
    return tables


def _parse_doc_blocks() -> dict[str, list[str]]:
    """Parse the machine-readable column blocks from docs/SCHEMA.md.

    Each documented relation is declared in a fenced ``text`` block of the
    form::

        relation: <name>
        columns: a, b, c
    """
    import re

    text = SCHEMA_DOC.read_text(encoding="utf-8")
    pattern = re.compile(
        r"relation:\s*(?P<name>\w+)\s*\ncolumns:\s*(?P<columns>[^\n]+)",
    )
    documented: dict[str, list[str]] = {}
    for match in pattern.finditer(text):
        documented[match.group("name")] = [
            column.strip()
            for column in match.group("columns").split(",")
            if column.strip()
        ]
    return documented


def test_schema_doc_exists() -> None:
    """docs/SCHEMA.md must be tracked, not a local-only convenience."""
    assert SCHEMA_DOC.is_file(), (
        "docs/SCHEMA.md is missing; the schema contract must be documented in-repo"
    )


def test_schema_doc_covers_every_build_table_and_column(tmp_path: Path) -> None:
    """Every SQLite table built by build.py must be documented exactly."""
    documented = _parse_doc_blocks()
    for table, columns in _build_tables(tmp_path).items():
        assert table in documented, f"docs/SCHEMA.md does not document table {table!r}"
        assert documented[table] == columns, (
            f"docs/SCHEMA.md columns for {table!r} drifted from build.py: "
            f"documented={documented[table]} actual={columns}"
        )


def test_schema_doc_covers_shot_corpus_columns() -> None:
    """The shot-corpus parquet contract from corpus.py must be documented.

    The corpus is the delivered shot-level schema (issue #17): identity
    columns, per-metric native columns, the unconverted apex passthrough, and
    the native_json audit payload.
    """
    documented = _parse_doc_blocks()
    expected = [
        *IDENTITY_COLUMNS,
        *CORPUS_COLUMN_MAP,
        *PASSTHROUGH_COLUMNS,
        "native_json",
    ]
    assert "shot_corpus" in documented, (
        "docs/SCHEMA.md does not document the shot_corpus parquet relation"
    )
    assert documented["shot_corpus"] == expected, (
        f"docs/SCHEMA.md shot_corpus columns drifted from corpus.py: "
        f"documented={documented['shot_corpus']} expected={expected}"
    )


def test_schema_doc_states_aggregate_group_mean_contract() -> None:
    """The hard aggregate contract must be documented next to the tables."""
    text = SCHEMA_DOC.read_text(encoding="utf-8")
    assert "aggregation_level" in text and "group_mean" in text, (
        "docs/SCHEMA.md must state the metric_observations group_mean hard contract"
    )


def test_schema_doc_states_caddieset_license_basis() -> None:
    """The first shot-level source must be documented with its license basis."""
    text = SCHEMA_DOC.read_text(encoding="utf-8")
    assert "caddieset_github" in text, (
        "docs/SCHEMA.md must document the first shot-level source, caddieset_github"
    )
    assert "MIT" in text, "the CaddieSet MIT basis must be stated"
    assert "unidentified camera-based" in text or "Unspecified camera-based" in text, (
        "the honest vendor treatment of CaddieSet's monitor must be stated"
    )


@pytest.mark.parametrize(
    ("expected_column", "table"),
    [
        ("aggregation_level", "metric_observations"),
        ("native_json", "shot_corpus"),
        ("source_id", "sources"),
    ],
)
def test_parse_doc_blocks_recovers_expected_contract(
    expected_column: str, table: str
) -> None:
    """The doc parser must find the expected contract anchors (guards drift)."""
    documented = _parse_doc_blocks()
    assert table in documented
    assert expected_column in documented[table]
