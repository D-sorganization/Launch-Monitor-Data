# Launch Monitor Data

An open, provenance-first database for comparing golf launch-monitor outputs and
ball-flight models.

The database currently contains:

- **56** traceable sources: official vendor documentation for TrackMan
  (including iO), FlightScope, Foresight (including Falcon), Garmin (R10 and
  R50), Rapsodo, SkyTrak, Uneekor, Bushnell, Full Swing, Voice Caddie, and
  Square Golf; peer-reviewed studies; and hash-pinned public shot-level
  datasets;
- **261** source-backed vendor/field availability records across twelve
  vendors;
- **207 matched shots** from a CC BY 4.0 TrackMan 4 versus FlightScope Mevo+
  study, represented without pretending published aggregates are raw shots;
- **57** published club/metric comparisons and **114** normalized
  monitor-specific aggregate observations;
- catalog entries with verified SHA-256 pins for more than a dozen public
  shot-level datasets (TrackMan, Mevo+, Garmin R10/R50, SkyTrak, Rapsodo
  MLM2PRO, Square Golf, Awesome Golf, and the MIT-licensed CaddieSet corpus)
  that are indexed but not copied where their repositories lack a license;
- an optional `data/studies/aggregate_observations.csv` ingestion path for
  redistributable single-monitor group statistics, validated fail-closed;
- **534 published reference values** in a dedicated `published_references`
  table: the TrackMan PGA and LPGA tour-averages tables (classic and 2023
  vintages), amateur and handicap-group figures, Combine benchmarks, and
  press-published numbers for more than 25 named tour players — every row
  cited, confidence-graded, and kept separate from the study observations;
- deterministic CSV and SQLite builds using the canonical metric names and SI
  units used by UpstreamDrift's `launch_monitor` package.

## Start Here

```powershell
python -m pip install -e .
launch-monitor-data validate
launch-monitor-data build --output database
python -m pytest
```

The committed database artifacts are:

- `database/launch_monitor_data.sqlite` — normalized queryable database;
- `database/study_comparisons.csv` — paired published statistics;
- `database/metric_observations.csv` — long-form aggregate observations;
- `database/upstreamdrift_aggregate_metrics.csv` — UpstreamDrift-compatible
  metric vocabulary and canonical units;
- `database/source_catalog.csv` and `database/vendor_fields.csv` — provenance
  and field-availability tables.

## What the Data Mean

The current redistributable comparison data are **published aggregate
statistics**, not individual swings. `aggregation_level=group_mean` is a hard
contract. Do not train a shot-level neural network by expanding each mean into
`sample_count` duplicate rows.

The TrackMan 4 and Mevo+ observations are matched at the study level: both
monitors observed the same retained shots. The paper excluded incomplete shots,
severe mishits, and any shot for which either unit reported estimated spin.

## Provenance Policy

Every observation must join to `sources.source_id`. Every source records a URL,
access date, monitor identity, granularity, reported sample count, license or
rights status, and limitations. The build fails closed when:

- a source or metric reference is unknown;
- a redistributable source lacks a license;
- required numeric or sample-count fields are invalid; or
- a vendor-field mapping lacks evidence.

`reference_only` means the source is useful and public but is not copied into
the redistributable observation tables. Public accessibility is not treated as
permission to redistribute.

## UpstreamDrift Compatibility

Metric names and canonical units mirror UpstreamDrift PR
[`#8343`](https://github.com/D-sorganization/UpstreamDrift/pull/8343): speeds in
metres per second, distances in metres, angles in radians, spin in radians per
second, and time in seconds. See
[`docs/UPSTREAMDRIFT_INTEGRATION.md`](docs/UPSTREAMDRIFT_INTEGRATION.md).

## Scope and Scientific Caution

This repository is an evidence substrate, not proof of which vendor is
"correct." A monitor can measure some launch variables, estimate other values,
and predict flight/roll under vendor-specific environmental assumptions.
Cross-monitor differences can also reflect alignment, indoor geometry, ball
type, metallic dots, firmware, software, normalization, and filtering.

Read [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) before model fitting and
[`CONTRIBUTING.md`](CONTRIBUTING.md) before donating data.

The optional hash-verified workflow for the unlicensed public TrackMan corpus is
documented in
[`docs/REFERENCE_ONLY_ACQUISITION.md`](docs/REFERENCE_ONLY_ACQUISITION.md).

## Licensing

Code is MIT licensed. Database rights and extracted data are licensed under CC
BY 4.0 only where the source permits redistribution; attribution and per-source
exceptions are in [`DATA_LICENSE.md`](DATA_LICENSE.md). Trademarks belong to
their respective owners. This project is not affiliated with any launch-monitor
manufacturer.
