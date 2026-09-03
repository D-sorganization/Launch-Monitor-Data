# Schema

This document is the tracked schema contract for the Launch Monitor Data
repository and the private launch-monitor authority it pins. It is enforced by
`tests/test_schema_doc.py`: whenever `build.py` creates a table or `corpus.py`
maps a column that this document does not list — or vice versa — CI fails.

Two relations families exist:

1. **The aggregate database** — built by the public code in
   `launch_monitor_data.build` from validated, redistributable source data.
   Real databases are produced and stored only inside the private authority.
2. **The shot-level corpus** — the source-partitioned Parquet dataset
   (`data/authority/database/shot_corpus_parquet/`) maintained in the private
   authority and read by the public code in `launch_monitor_data.corpus`.

Issue #17 asked for a `shot_observations` table; the delivered design is the
Parquet shot corpus documented below (read through `load_shots`), which
carries per-shot rows with preserved native payloads. The aggregate contract
is untouched by design.

## The aggregate database

`metric_observations` enforces the **group-mean hard contract**: every row
carries `aggregation_level`, constrained by a `CHECK` to the single value
`'group_mean'`. Row-level data never enters this table; it lives in the shot
corpus instead.

### Tables

```text
relation: sources
columns: source_id, title, source_type, url, doi, publication_date, accessed_date, monitors, record_granularity, reported_n, redistribution_status, license_spdx, license_url, pinned_ref, sha256, limitations
```

```text
relation: vendor_fields
columns: vendor, model_scope, metric, availability, measurement_claim, source_id, notes
```

```text
relation: study_comparisons
columns: source_id, club, sample_count, metric, source_unit, trackman_mean, trackman_sd, trackman_min, trackman_max, flightscope_mean, flightscope_sd, flightscope_min, flightscope_max, mean_difference_trackman_minus_flightscope, sd_difference, mape_percent, icc_consistency, icc_absolute, pearson_r, measurement_status, environment, software_version
```

```text
relation: metric_observations
columns: observation_id, source_id, monitor_vendor, monitor_model, software_version, environment, cohort, club, metric, aggregation_level, sample_count, measurement_status, reported_mean, reported_sd, reported_unit, canonical_mean, canonical_sd, canonical_unit, matched_shots
```

```text
relation: published_references
columns: reference_id, source_id, population_type, population, context, monitor, year, club, metric_native, metric, value, source_unit, canonical_value, canonical_unit, value_type, confidence, citation_urls, notes
```

`sources.source_id` is the join key for every other table. Canonical metric
names and units are defined once in `launch_monitor_data.contracts` and kept
in name-and-unit parity with UpstreamDrift's `launch_monitor` schema.

## The shot-level corpus

The shot corpus is a Hive-partitioned Parquet dataset
(`source_id=<id>/part-*.parquet`) inside the private authority. Identity
columns identify a shot; metric columns store source-native units (mph, deg,
rpm, yd) that `load_shots` converts to the canonical SI contract;
`native_json` preserves the complete native payload of every shot so raw and
canonical values stay separable, per the review gates.

```text
relation: shot_corpus
columns: source_id, monitor, club, file, row_index, captured_at, club_speed_mph, ball_speed_mph, smash_factor, launch_angle_deg, launch_direction_deg, spin_rate_rpm, back_spin_rpm, side_spin_rpm, spin_axis_deg, attack_angle_deg, club_path_deg, face_angle_deg, carry_yd, total_yd, descent_angle_deg, lateral_carry_yd, flight_time_s, apex_native, native_json
```

`apex_native` passes through unconverted because its unit varies by source.

### The first shot-level source: `caddieset_github`

CaddieSet (https://github.com/damilab/CaddieSet) is ingested under its MIT
license, byte-pinned at commit `3c73d9d40580bb8a5a10711ad1fa10735a205ffe`
with per-file SHA-256 recorded in the authority's
`acquisition_manifest.json`. The dataset's launch monitor is not identified
by its publisher, so the corpus records the honest value
`Unspecified camera-based launch monitor` in `monitor` rather than
inventing a vendor attribution.

Anonymization was verified against the redistributed rows: the source's only
person-level field is `GolferId`, carried in `native_json` as the integers
1 through 8. No names, contact data, or device serials appear in any
CaddieSet row. The publisher's requested citation (CVPRW 2025) is recorded
in `DATA_LICENSE.md`.

## Where data lives

This public repository distributes no launch-monitor datasets. The private
authority (commit-pinned by `private_data.lock.json`) stores source
snapshots, normalized databases, and row-level derived artifacts; all data
commands fail closed without an authenticated checkout. See
`DATA_LICENSE.md` for the license boundary and `docs/PRIVATE_ACCESS.md`
for access.