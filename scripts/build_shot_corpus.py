"""Build a local, non-redistributed shot-level corpus from cataloged sources.

Clones every shot-level GitHub source pinned in ``data/source_catalog.csv`` at
its exact pinned commit, parses the native exports into one queryable SQLite
database, and writes everything under ``local_data/`` which is git-ignored.

Nothing this script downloads is committed or redistributed: the corpus is
reproduced on demand from the original hosts, which is the same posture as
``scripts/fetch_reference_only.py``. Player-identifying columns (names,
emails) are replaced with stable per-source labels before storage.

Usage:
    python scripts/build_shot_corpus.py [--output local_data]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

PII_COLUMNS = {
    "player",
    "golfer",
    "email",
    "name",
    "player name",
}

# Header synonyms mapped to common extracted fields (values kept in native
# units; unit noted in the column name).
FIELD_SYNONYMS: dict[str, tuple[str, ...]] = {
    "club_speed_mph": (
        "club speed",
        "club_mph",
        "clubspeed",
        "clubhead speed",
        "swing speed",
    ),
    "ball_speed_mph": ("ball speed", "ball_mph", "ballspeed"),
    "smash_factor": ("smash factor", "smash", "smash_factor", "smashfactor"),
    "launch_angle_deg": (
        "launch angle",
        "launch v",
        "launch_v",
        "vertical launch",
        "launch",
    ),
    "launch_direction_deg": (
        "launch direction",
        "launch h",
        "launch_h",
        "horizontal launch",
        "push/pull",
        "side angle",
    ),
    "spin_rate_rpm": ("spin rate", "spin_rpm", "total spin"),
    "back_spin_rpm": ("back spin", "backspin"),
    "side_spin_rpm": ("side spin", "sidespin"),
    "spin_axis_deg": ("spin axis",),
    "attack_angle_deg": ("attack angle", "aoa"),
    "club_path_deg": ("club path",),
    "face_angle_deg": ("face angle", "club face"),
    "carry_yd": (
        "carry",
        "carry distance",
        "carry_yds",
        "carry flat - length",
    ),
    "total_yd": ("total", "total distance", "total_yds"),
    "apex_native": (
        "apex",
        "apex height",
        "peak height",
        "height_ft",
        "max height - height",
    ),
    "descent_angle_deg": (
        "descent angle",
        "land angle",
        "landing angle",
        "carry flat - land. angle",
    ),
    "club": ("club", "club name", "club type"),
}

# Extracted columns are convenience values kept in source-native units (mostly
# imperial; apex_native varies by source). native_json is the ground truth.


@dataclass(frozen=True)
class ShotSource:
    source_id: str
    repo: str
    ref: str
    globs: tuple[str, ...]
    monitor: str
    notes: str = ""
    expected_sha256: dict[str, str] = field(default_factory=dict)


SOURCES: tuple[ShotSource, ...] = (
    ShotSource(
        "blackmore_trackman_10169",
        "tim-blackmore/launch-monitor-regression",
        "main",
        ("data.csv",),
        "TrackMan",
        "35-column native export with a units row",
        {
            "data.csv": (
                "fae80d325e69c928debcbbbacd908c1e"
                "4a8b0d44d5cd5290a2bbad95b83cae04"
            )
        },
    ),
    ShotSource(
        "dmombo_mevo_plus_db",
        "dmombo/GolfStats",
        "0c68cf24adc272d0007ed13a83de64f582fba859",
        ("FS_Golf_DB.csv",),
        "FlightScope Mevo+",
        "FlightScope Cloud export; player names anonymized on load",
        {
            "FS_Golf_DB.csv": (
                "057abd9ade83e1c3dd2fffded2def01f"
                "ba41487b548ef629866f071b8160e872"
            )
        },
    ),
    ShotSource(
        "jacqzang_trackman_practice",
        "jacqzang/golf_swing_analysis",
        "5899f5af49fe48883cc92f476d44eb6713dd7e0b",
        ("data/processed/cleaned_shots.csv",),
        "TrackMan",
    ),
    ShotSource(
        "jgamblin_garmin_r10_sessions",
        "jgamblin/golf",
        "479666465683a056c19bedb91338f0ed8f80ea60",
        ("Data/*.csv",),
        "Garmin Approach R10",
    ),
    ShotSource(
        "hoffpauir_skytrak_sessions",
        "RobinCHoffpauir/Golf",
        "941f1b426c54839da8b273a217fad59f0966a33a",
        ("sessions/*.csv",),
        "SkyTrak (schema match)",
    ),
    ShotSource(
        "sghill_mevo_range",
        "sghill/golf",
        "fd9c09e91f2ed4dc7678b8ff1848fb30ab5575ff",
        ("range/**/*.csv",),
        "FlightScope Mevo",
    ),
    ShotSource(
        "callejo_trackman_sessions",
        "JUAN-CALLEJO/Trackman_Interactive_App",
        "ccdb4f0b71792463b87d5ded5f43d49dfa8881b7",
        ("player_data.csv",),
        "TrackMan",
        "player names and emails anonymized on load",
    ),
    ShotSource(
        "caddieset_github",
        "damilab/CaddieSet",
        "3c73d9d40580bb8a5a10711ad1fa10735a205ffe",
        ("data/**/*.csv", "data/*.csv"),
        "Unspecified camera-based launch monitor",
        "MIT licensed",
    ),
    ShotSource(
        "j72jones_trackman_7iron",
        "j72jones/stochasticGolf",
        "61bdf24952d12308fb06d44cd6bc96314f9f2f27",
        ("trackman-csv-export-20230807.Normalized.csv",),
        "TrackMan",
        "sep= prefix and units row",
    ),
    ShotSource(
        "mmender2_mlm2pro_clubs",
        "mmender2/GolfAnalysis",
        "007b799785a991b2e3b35f8a37a2eb059b1f73cf",
        ("*.csv",),
        "Rapsodo MLM2PRO (schema match)",
    ),
    ShotSource(
        "ummerr_garmin_r50_ledger",
        "ummerr/mackenzie",
        "aa120a213231441eb50a1cbafa2cdcc23890f86f",
        ("yardages/data/raw/*.csv",),
        "Garmin Approach R50",
    ),
    ShotSource(
        "tomcox_garmin_range",
        "Tom-Cox-1/Driving-Range-Data-Analysis",
        "e0131bdad74898ab601e59ff90ed7b6127b084a0",
        ("data/DrivingRangeData.csv",),
        "Garmin Approach R10 (schema match)",
    ),
    ShotSource(
        "mpgentleman_awesome_golf_sample",
        "mpgentleman/GolfStats",
        "86b072baa73e71ac07bdc48e2d4255be7004a6c2",
        ("ags-shots-sample.csv",),
        "Awesome Golf app",
    ),
    ShotSource(
        "bluedaniel_square_gapping",
        "bluedaniel/square-stats",
        "11a4d7225cf5a13633a3afa7e8c433eb250c02a6",
        ("test-fixtures/*.csv",),
        "Square Golf",
    ),
    ShotSource(
        "openflight_session_log",
        "jewbetcha/openflight",
        "89211cb8fe621da86914d807f1b89419ffe3afda",
        ("session_logs/*.csv",),
        "OpenFlight DIY Doppler radar",
        "AGPL-3.0 licensed; TrackMan-compatible export",
    ),
)


def _run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True, capture_output=True)


def _clone(source: ShotSource, raw_dir: Path) -> Path:
    target = raw_dir / source.source_id
    if (target / ".git").is_dir():
        return target
    target.mkdir(parents=True, exist_ok=True)
    url = f"https://github.com/{source.repo}"
    _run(["git", "init", "-q"], cwd=target)
    _run(["git", "remote", "add", "origin", url], cwd=target)
    _run(["git", "fetch", "-q", "--depth", "1", "origin", source.ref], cwd=target)
    _run(["git", "checkout", "-q", "FETCH_HEAD"], cwd=target)
    return target


def _verify_hashes(source: ShotSource, checkout: Path) -> None:
    for relative, expected in source.expected_sha256.items():
        digest = hashlib.sha256((checkout / relative).read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError(
                f"{source.source_id}: {relative} sha256 {digest} does not "
                f"match pinned {expected}"
            )


def _decode(path: Path) -> str:
    text = path.read_bytes().decode("utf-8-sig", errors="replace")
    return text.lstrip("﻿")


def _read_rows(path: Path) -> list[dict[str, str]]:
    text = _decode(path)
    lines = text.splitlines()
    if not lines:
        return []
    if lines[0].strip().lower().startswith("sep="):
        lines = lines[1:]
    if not lines:
        return []
    reader = csv.reader(io.StringIO("\n".join(lines)))
    table = [row for row in reader if any(cell.strip() for cell in row)]
    if len(table) < 2:
        return []
    known = {
        synonym for synonyms in FIELD_SYNONYMS.values() for synonym in synonyms
    }

    def header_score(row: list[str]) -> int:
        return sum(
            1
            for cell in row
            if re.sub(r"\(.*?\)", "", cell).strip().lower() in known
        )

    # Some exports carry metadata lines above the real header row.
    header_index = 0
    for index, row in enumerate(table[:5]):
        if header_score(row) >= 3:
            header_index = index
            break
    header = [cell.strip() for cell in table[header_index]]
    body = table[header_index + 1 :]
    # TrackMan exports carry a units row like "[mph]" directly under the header.
    if body and all(
        not cell.strip() or re.fullmatch(r"\[.*\]", cell.strip())
        for cell in body[0]
    ):
        units = [cell.strip().strip("[]") for cell in body[0]]
        header = [
            f"{name} ({unit})" if unit and name else name
            for name, unit in zip(header, units, strict=False)
        ]
        body = body[1:]
    rows = []
    for row in body:
        record = {}
        for index, name in enumerate(header):
            if not name:
                continue
            record[name] = row[index].strip() if index < len(row) else ""
        rows.append(record)
    return rows


def _number(value: str) -> float | None:
    cleaned = value.replace(",", "").replace("yds", "").replace("mph", "")
    cleaned = cleaned.strip()
    sign = 1.0
    # Directional exports use leading or trailing L/R for left/right.
    if re.fullmatch(r"[LR][0-9.+-]+", cleaned):
        sign = -1.0 if cleaned[0] == "L" else 1.0
        cleaned = cleaned[1:]
    elif re.fullmatch(r"[0-9.+-]+\s*[LR]", cleaned):
        sign = -1.0 if cleaned.rstrip()[-1] == "L" else 1.0
        cleaned = cleaned.rstrip()[:-1].strip()
    if not cleaned or cleaned in {"-", "--", "n/a", "N/A"}:
        return None
    try:
        return sign * float(cleaned)
    except ValueError:
        return None


def _extract(record: dict[str, str]) -> dict[str, object]:
    lowered = {
        re.sub(r"\(.*?\)", "", key).strip().lower(): value
        for key, value in record.items()
    }
    extracted: dict[str, object] = {}
    for target, synonyms in FIELD_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in lowered and lowered[synonym]:
                if target == "club":
                    extracted[target] = lowered[synonym]
                else:
                    number = _number(lowered[synonym])
                    if number is not None:
                        extracted[target] = number
                break
    return extracted


def _anonymize(
    record: dict[str, str], labels: dict[str, str], source_id: str
) -> dict[str, str]:
    cleaned = {}
    for key, value in record.items():
        if key.strip().lower() in PII_COLUMNS:
            if value:
                label = labels.setdefault(
                    value, f"{source_id}_player_{len(labels) + 1}"
                )
                cleaned[key] = label
        else:
            cleaned[key] = value
    return cleaned


def build_corpus(output_dir: Path) -> None:
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    database_path = output_dir / "shot_corpus.sqlite"
    if database_path.exists():
        database_path.unlink()
    connection = sqlite3.connect(database_path)
    connection.executescript(
        """
        CREATE TABLE shots (
            source_id TEXT NOT NULL,
            monitor TEXT NOT NULL,
            file TEXT NOT NULL,
            row_index INTEGER NOT NULL,
            club TEXT,
            club_speed_mph REAL,
            ball_speed_mph REAL,
            smash_factor REAL,
            launch_angle_deg REAL,
            launch_direction_deg REAL,
            spin_rate_rpm REAL,
            back_spin_rpm REAL,
            side_spin_rpm REAL,
            spin_axis_deg REAL,
            attack_angle_deg REAL,
            club_path_deg REAL,
            face_angle_deg REAL,
            carry_yd REAL,
            total_yd REAL,
            apex_native REAL,
            descent_angle_deg REAL,
            native_json TEXT NOT NULL
        );
        CREATE INDEX shots_lookup ON shots(source_id, club);
        """
    )
    numeric_columns = [
        "club_speed_mph", "ball_speed_mph", "smash_factor",
        "launch_angle_deg", "launch_direction_deg", "spin_rate_rpm",
        "back_spin_rpm", "side_spin_rpm", "spin_axis_deg", "attack_angle_deg",
        "club_path_deg", "face_angle_deg", "carry_yd", "total_yd",
        "apex_native", "descent_angle_deg",
    ]
    totals: dict[str, int] = {}
    for source in SOURCES:
        try:
            checkout = _clone(source, raw_dir)
            _verify_hashes(source, checkout)
        except (subprocess.CalledProcessError, ValueError) as error:
            print(f"SKIP {source.source_id}: {error}", file=sys.stderr)
            continue
        labels: dict[str, str] = {}
        count = 0
        files: list[Path] = []
        for pattern in source.globs:
            files.extend(sorted(checkout.glob(pattern)))
        for path in dict.fromkeys(files):
            for index, record in enumerate(_read_rows(path)):
                cleaned = _anonymize(record, labels, source.source_id)
                extracted = _extract(cleaned)
                if not any(key in extracted for key in numeric_columns):
                    continue
                connection.execute(
                    "INSERT INTO shots (source_id, monitor, file, row_index, "
                    "club, " + ", ".join(numeric_columns) + ", native_json) "
                    "VALUES ("
                    + ", ".join("?" for _ in range(5 + len(numeric_columns) + 1))
                    + ")",
                    [
                        source.source_id,
                        source.monitor,
                        str(path.relative_to(checkout)),
                        index,
                        extracted.get("club"),
                        *[extracted.get(column) for column in numeric_columns],
                        json.dumps(cleaned, ensure_ascii=False),
                    ],
                )
                count += 1
        totals[source.source_id] = count
        print(f"{source.source_id}: {count} rows")
    connection.commit()
    grand_total = sum(totals.values())
    print(f"TOTAL: {grand_total} rows in {database_path}")
    connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPOSITORY_ROOT / "local_data",
        help="Directory for clones and the corpus database (git-ignored)",
    )
    args = parser.parse_args()
    build_corpus(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
