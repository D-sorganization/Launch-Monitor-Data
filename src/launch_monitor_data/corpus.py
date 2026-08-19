"""Read the private shot corpus into canonical-schema analysis frames.

The corpus is the source-partitioned Parquet dataset maintained in the private
data authority (``data/authority/database/shot_corpus_parquet/``). Its numeric
columns are stored in source-native imperial units (mph, deg, rpm, yd); this
module converts them to the canonical SI contract from
:mod:`launch_monitor_data.contracts` so frames drop straight into
UpstreamDrift's ``launch_monitor`` analytics, which shares the same metric
names and units.

Requires the optional ``corpus`` extra::

    pip install "launch-monitor-data[corpus]"

Example::

    from launch_monitor_data.corpus import load_shots

    shots = load_shots(sources=["blackmore_trackman_10169"])
    shots[["ball_speed", "carry_distance"]].describe()  # m/s, m
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from launch_monitor_data.paths import authority_dir, require_private_authority
from launch_monitor_data.units import conversion_factor

if TYPE_CHECKING:  # pragma: no cover - typing only
    import pandas as pd

# Corpus column -> (canonical metric, source unit). Every corpus numeric
# column except apex_native, whose unit varies by source and is therefore
# passed through unconverted under its original name.
CORPUS_COLUMN_MAP: dict[str, tuple[str, str]] = {
    "club_speed_mph": ("club_speed", "mph"),
    "ball_speed_mph": ("ball_speed", "mph"),
    "smash_factor": ("smash_factor", "1"),
    "launch_angle_deg": ("launch_angle", "deg"),
    "launch_direction_deg": ("launch_direction", "deg"),
    "spin_rate_rpm": ("spin_rate", "rpm"),
    "back_spin_rpm": ("back_spin", "rpm"),
    "side_spin_rpm": ("side_spin", "rpm"),
    "spin_axis_deg": ("spin_axis", "deg"),
    "attack_angle_deg": ("attack_angle", "deg"),
    "club_path_deg": ("club_path", "deg"),
    "face_angle_deg": ("face_angle", "deg"),
    "carry_yd": ("carry_distance", "yd"),
    "total_yd": ("total_distance", "yd"),
    "descent_angle_deg": ("descent_angle", "deg"),
    "lateral_carry_yd": ("lateral_carry", "yd"),
    "flight_time_s": ("flight_time", "s"),
}

IDENTITY_COLUMNS: tuple[str, ...] = (
    "source_id",
    "monitor",
    "club",
    "file",
    "row_index",
    # ISO-8601 capture instant where the source provides one; absent from a
    # corpus built before the #18/#19 extraction, hence the tolerant select.
    "captured_at",
)

PASSTHROUGH_COLUMNS: tuple[str, ...] = ("apex_native",)


def corpus_dataset_path() -> Path:
    """Path of the Parquet corpus inside the synced private authority."""
    return authority_dir() / "database" / "shot_corpus_parquet"


def _require_pyarrow_dataset() -> Any:
    try:
        import pyarrow.dataset as pyarrow_dataset
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise ImportError(
            "reading the shot corpus requires the optional corpus extra; "
            'install it with: pip install "launch-monitor-data[corpus]"'
        ) from exc
    return pyarrow_dataset


def available_sources() -> list[str]:
    """List the source_id partitions present in the synced corpus."""
    dataset_dir = _require_corpus_dir()
    return sorted(
        entry.name.split("=", 1)[1]
        for entry in dataset_dir.iterdir()
        if entry.is_dir() and entry.name.startswith("source_id=")
    )


def _require_corpus_dir() -> Path:
    require_private_authority()
    dataset_dir = corpus_dataset_path()
    if not dataset_dir.is_dir():
        raise FileNotFoundError(
            f"shot corpus dataset is missing from {dataset_dir}; the pinned "
            "commit in private_data.lock.json may predate the Parquet corpus "
            "- bump it to a Launch-Monitor-Flight-Model-Campaign commit that "
            "contains data/authority/database/shot_corpus_parquet/ and re-run "
            "`python scripts/sync_private_data.py sync`"
        )
    return dataset_dir


def load_shots(
    *,
    sources: list[str] | None = None,
    metrics: list[str] | None = None,
    canonical_units: bool = True,
    include_native_json: bool = False,
) -> pd.DataFrame:
    """Load corpus shots as one analysis-ready DataFrame.

    Args:
        sources: Optional source_id allowlist; ``None`` loads every source.
        metrics: Optional canonical metric-name allowlist (for example
            ``["ball_speed", "carry_distance"]``); ``None`` loads all mapped
            metrics. Pruning here is pushed down to the Parquet reader.
        canonical_units: When ``True`` (default), numeric columns are renamed
            to canonical metric names and converted to SI canonical units.
            When ``False``, source-native column names and units are kept.
        include_native_json: Also load the per-shot ``native_json`` audit
            column (large; off by default).

    Returns:
        DataFrame with identity columns, the requested metric columns, the
        unconverted ``apex_native`` passthrough, and an ``observation_kind``
        column fixed to ``"shot"``.
    """
    pyarrow_dataset = _require_pyarrow_dataset()
    dataset_dir = _require_corpus_dir()

    selected_map = dict(CORPUS_COLUMN_MAP)
    if metrics is not None:
        unknown = set(metrics) - {name for name, _ in CORPUS_COLUMN_MAP.values()}
        if unknown:
            raise ValueError(f"Unknown corpus metrics requested: {sorted(unknown)}")
        selected_map = {
            column: (name, unit)
            for column, (name, unit) in CORPUS_COLUMN_MAP.items()
            if name in metrics
        }

    columns = [
        column
        for column in (*IDENTITY_COLUMNS, *selected_map, *PASSTHROUGH_COLUMNS)
        if column != "source_id"
    ]
    if include_native_json:
        columns.append("native_json")

    dataset = pyarrow_dataset.dataset(
        dataset_dir, format="parquet", partitioning="hive"
    )
    # A corpus pinned before a column was introduced simply lacks it; select
    # what the dataset actually has rather than failing the whole read.
    available = set(dataset.schema.names)
    filter_expression = None
    if sources is not None:
        missing = set(sources) - set(available_sources())
        if missing:
            raise ValueError(f"Unknown corpus sources requested: {sorted(missing)}")
        filter_expression = pyarrow_dataset.field("source_id").isin(sources)
    table = dataset.to_table(
        columns=[name for name in ["source_id", *columns] if name in available],
        filter=filter_expression,
    )
    frame = table.to_pandas()

    if canonical_units:
        conversions = {
            column: (name, conversion_factor(unit, name))
            for column, (name, unit) in selected_map.items()
        }
        conversions = {
            column: value
            for column, value in conversions.items()
            if column in frame.columns
        }
        for column, (_, factor) in conversions.items():
            frame[column] = frame[column] * factor
        frame = frame.rename(
            columns={column: name for column, (name, _) in conversions.items()}
        )

    frame["observation_kind"] = "shot"
    return frame  # type: ignore[no-any-return]
