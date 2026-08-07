"""Build normalized CSV and SQLite database artifacts from canonical source files."""

from __future__ import annotations

import csv
import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from launch_monitor_data.paths import (
    AGGREGATES,
    COMPARISONS,
    SOURCE_CATALOG,
    VENDOR_FIELDS,
)
from launch_monitor_data.units import to_canonical
from launch_monitor_data.validation import validate_repository_data


@dataclass(frozen=True)
class BuildResult:
    output_dir: Path
    source_count: int
    vendor_count: int
    comparison_count: int
    observation_count: int


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty artifact: {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _observation_id(
    source_id: str,
    club: str,
    metric: str,
    vendor: str,
    cohort: str = "",
    model: str = "",
) -> str:
    payload = f"{source_id}|{club}|{metric}|{vendor}".encode()
    if cohort or model:
        payload = f"{source_id}|{cohort}|{club}|{metric}|{vendor}|{model}".encode()
    return hashlib.sha256(payload).hexdigest()[:24]


def _normalize_observations(
    comparisons: list[dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    monitor_columns = (
        ("TrackMan", "TrackMan 4", "trackman"),
        ("FlightScope", "Mevo+", "flightscope"),
    )
    for row in comparisons:
        for vendor, model, prefix in monitor_columns:
            reported_mean = float(row[f"{prefix}_mean"])
            reported_sd = float(row[f"{prefix}_sd"])
            canonical_mean, canonical_unit = to_canonical(
                reported_mean, row["source_unit"], row["metric"]
            )
            canonical_sd, _ = to_canonical(
                reported_sd, row["source_unit"], row["metric"]
            )
            rows.append(
                {
                    "observation_id": _observation_id(
                        row["source_id"], row["club"], row["metric"], vendor
                    ),
                    "source_id": row["source_id"],
                    "monitor_vendor": vendor,
                    "monitor_model": model,
                    "software_version": row["software_version"],
                    "environment": row["environment"],
                    "cohort": "single_participant",
                    "club": row["club"],
                    "metric": row["metric"],
                    "aggregation_level": "group_mean",
                    "sample_count": int(row["sample_count"]),
                    "measurement_status": row["measurement_status"],
                    "reported_mean": reported_mean,
                    "reported_sd": reported_sd,
                    "reported_unit": row["source_unit"],
                    "canonical_mean": canonical_mean,
                    "canonical_sd": canonical_sd,
                    "canonical_unit": canonical_unit,
                    "matched_shots": 1,
                }
            )
    return rows


def _normalize_aggregates(
    aggregates: list[dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in aggregates:
        reported_mean = float(row["reported_mean"])
        reported_sd_text = row.get("reported_sd", "").strip()
        canonical_mean, canonical_unit = to_canonical(
            reported_mean, row["source_unit"], row["metric"]
        )
        reported_sd: object
        canonical_sd: object
        if reported_sd_text:
            reported_sd = float(reported_sd_text)
            canonical_sd, _ = to_canonical(
                float(reported_sd_text), row["source_unit"], row["metric"]
            )
        else:
            reported_sd = None
            canonical_sd = None
        rows.append(
            {
                "observation_id": _observation_id(
                    row["source_id"],
                    row["club"],
                    row["metric"],
                    row["monitor_vendor"],
                    row["cohort"],
                    row["monitor_model"],
                ),
                "source_id": row["source_id"],
                "monitor_vendor": row["monitor_vendor"],
                "monitor_model": row["monitor_model"],
                "software_version": row["software_version"],
                "environment": row["environment"],
                "cohort": row["cohort"],
                "club": row["club"],
                "metric": row["metric"],
                "aggregation_level": row["aggregation_level"],
                "sample_count": int(row["sample_count"]),
                "measurement_status": row["measurement_status"],
                "reported_mean": reported_mean,
                "reported_sd": reported_sd,
                "reported_unit": row["source_unit"],
                "canonical_mean": canonical_mean,
                "canonical_sd": canonical_sd,
                "canonical_unit": canonical_unit,
                "matched_shots": int(row["matched_shots"]),
            }
        )
    return rows


def _create_database(
    path: Path,
    sources: list[dict[str, str]],
    fields: list[dict[str, str]],
    comparisons: list[dict[str, str]],
    observations: list[dict[str, object]],
) -> None:
    if path.exists():
        path.unlink()
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE sources (
                source_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                source_type TEXT NOT NULL,
                url TEXT NOT NULL,
                doi TEXT,
                publication_date TEXT,
                accessed_date TEXT NOT NULL,
                monitors TEXT NOT NULL,
                record_granularity TEXT NOT NULL,
                reported_n INTEGER,
                redistribution_status TEXT NOT NULL,
                license_spdx TEXT,
                license_url TEXT,
                pinned_ref TEXT,
                sha256 TEXT,
                limitations TEXT NOT NULL
            );
            CREATE TABLE vendor_fields (
                vendor TEXT NOT NULL,
                model_scope TEXT NOT NULL,
                metric TEXT NOT NULL,
                availability TEXT NOT NULL,
                measurement_claim TEXT NOT NULL,
                source_id TEXT NOT NULL REFERENCES sources(source_id),
                notes TEXT NOT NULL,
                PRIMARY KEY (vendor, model_scope, metric)
            );
            CREATE TABLE study_comparisons (
                source_id TEXT NOT NULL REFERENCES sources(source_id),
                club TEXT NOT NULL,
                sample_count INTEGER NOT NULL,
                metric TEXT NOT NULL,
                source_unit TEXT NOT NULL,
                trackman_mean REAL NOT NULL,
                trackman_sd REAL NOT NULL,
                trackman_min REAL NOT NULL,
                trackman_max REAL NOT NULL,
                flightscope_mean REAL NOT NULL,
                flightscope_sd REAL NOT NULL,
                flightscope_min REAL NOT NULL,
                flightscope_max REAL NOT NULL,
                mean_difference_trackman_minus_flightscope REAL NOT NULL,
                sd_difference REAL NOT NULL,
                mape_percent REAL NOT NULL,
                icc_consistency REAL NOT NULL,
                icc_absolute REAL NOT NULL,
                pearson_r REAL NOT NULL,
                measurement_status TEXT NOT NULL,
                environment TEXT NOT NULL,
                software_version TEXT NOT NULL,
                PRIMARY KEY (source_id, club, metric)
            );
            CREATE TABLE metric_observations (
                observation_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL REFERENCES sources(source_id),
                monitor_vendor TEXT NOT NULL,
                monitor_model TEXT NOT NULL,
                software_version TEXT NOT NULL,
                environment TEXT NOT NULL,
                cohort TEXT NOT NULL,
                club TEXT NOT NULL,
                metric TEXT NOT NULL,
                aggregation_level TEXT NOT NULL
                    CHECK (aggregation_level = 'group_mean'),
                sample_count INTEGER NOT NULL CHECK (sample_count > 0),
                measurement_status TEXT NOT NULL,
                reported_mean REAL NOT NULL,
                reported_sd REAL,
                reported_unit TEXT NOT NULL,
                canonical_mean REAL NOT NULL,
                canonical_sd REAL,
                canonical_unit TEXT NOT NULL,
                matched_shots INTEGER NOT NULL CHECK (matched_shots IN (0, 1))
            );
            CREATE INDEX metric_observations_lookup
                ON metric_observations(metric, monitor_vendor, club);
            """
        )
        for table, rows in (
            ("sources", sources),
            ("vendor_fields", fields),
            ("study_comparisons", comparisons),
            ("metric_observations", observations),
        ):
            columns = list(rows[0])
            placeholders = ", ".join("?" for _ in columns)
            connection.executemany(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                ([row[column] for column in columns] for row in rows),
            )


def build_database(output_dir: str | Path) -> BuildResult:
    """Build all derived artifacts from validated, redistributable source data."""
    report = validate_repository_data()
    if not report.ok:
        message = "Repository data failed validation:\n" + "\n".join(report.errors)
        raise ValueError(message)
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    sources = _read(SOURCE_CATALOG)
    fields = _read(VENDOR_FIELDS)
    comparisons = _read(COMPARISONS)
    aggregates = _read(AGGREGATES) if AGGREGATES.is_file() else []
    observations = _normalize_observations(comparisons)
    observations.extend(_normalize_aggregates(aggregates))

    _write_csv(destination / "metric_observations.csv", observations)
    _write_csv(destination / "upstreamdrift_aggregate_metrics.csv", observations)
    _write_csv(destination / "source_catalog.csv", sources)
    _write_csv(destination / "vendor_fields.csv", fields)
    _write_csv(destination / "study_comparisons.csv", comparisons)
    _create_database(
        destination / "launch_monitor_data.sqlite",
        sources,
        fields,
        comparisons,
        observations,
    )
    return BuildResult(
        output_dir=destination,
        source_count=len(sources),
        vendor_count=len({row["vendor"] for row in fields}),
        comparison_count=len(comparisons),
        observation_count=len(observations),
    )
