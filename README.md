# Launch Monitor Data Access Client

This public repository contains share-safe schemas, validation/build code, and
an authenticated sync client. Real launch-monitor data, published value tables,
source snapshots, normalized databases, and row-level derived artifacts are
stored only in D-sorganization's private data authority.

## Authorized setup

```powershell
python scripts/sync_private_data.py sync
$env:LAUNCH_MONITOR_DATA_ROOT = `
  (Resolve-Path private_data/launch-monitor-authority).Path
launch-monitor-data validate
```

The sync client clones the private
`D-sorganization/Launch-Monitor-Flight-Model-Campaign` repository at the exact
commit `d469b8a427418fa00e99b0ad488e4310b067697d` recorded in
`private_data.lock.json`. It does not accept a moving branch
or silently download from third-party sources. Git ignores the checkout.

Users without private access can inspect and test the public code, but data
commands fail closed until an authorized checkout is present.

## Qualified capabilities and eligibility

Release A distinguishes the 261,666-row source inventory from scientifically
qualified cohorts. The locked authority reports 13,855 complete, non-imputed
five-input rows; outcome-specific agreement sample sizes are smaller. These are
vendor-output agreement cohorts, not independent ground truth.

Applications can inspect only hash-verified, data-free metadata from the
authenticated checkout:

```python
from launch_monitor_data import (
    load_capabilities,
    load_release_b_status,
    load_source_metric_eligibility,
    vendor_operation,
)

capabilities = load_capabilities()
trackman = vendor_operation("trackman", "model_agreement")
training = vendor_operation("trackman", "vendor_training")
assert trackman.allowed
assert not training.allowed
print(training.reasons)  # no approved repeating split group

matrix = load_source_metric_eligibility(vendor_key="trackman")
release_b = load_release_b_status()
assert release_b.planned_pairs == 252
assert release_b.triggered_pairs == 0
assert release_b.analyzed_pairs == 0
assert not release_b.confirmatory_ready
assert release_b.vendor_training_eligible_rows == 0
```

The API verifies the exact private commit, qualification schemas, policy/count
agreement, and SHA-256 hashes before returning aggregate or source/metric policy
metadata. It never returns shot rows. Unknown vendors, unknown operations,
missing metadata, commit drift, and hash drift fail closed. Current metadata
does not authorize within-player, longitudinal, strokes-gained, same-shot
cross-device, public-output, or vendor-surrogate training workflows. ShotLink
remains prohibited for vendor training and public output.

## Release B collection status

The pinned private authority contains a hash-verified structural schedule for
252 paired shots: 84 each for driver, 7-iron, and wedge. As of this exact
release, **0 of 252 pairs have been triggered or analyzed**, every ledger row is
`not_collected`, and `confirmatory_ready` is false. No vendor-training decision
or group-safe training row became eligible.

`load_release_b_status()` verifies the private status, schedule, ledger, pair
membership, cell counts, accounting, and existing eligibility matrix before
returning aggregate status. It never returns schedule, ledger, capture, or shot
rows. The structural schedule does not establish vendor agreement and must not
be described as collected evidence. Physical campaign parameters—including
the ball SKU, numeric speed bands, hardware/reference set, calibration
certificates, and placement plan—remain owner-controlled pre-pilot hold points.

## Working with the shot corpus

The private authority carries a source-partitioned Parquet corpus
(261,666 shots across 27 sources at the pinned authority commit). With the
`corpus` extra
installed (`pip install -e ".[corpus]"`), load it as an analysis-ready frame
in the canonical SI contract shared with UpstreamDrift's `launch_monitor`
analytics (angles in radians, speeds in m/s, spin in rad/s, distances in m):

```python
from launch_monitor_data.corpus import available_sources, load_shots

load_shots(metrics=["ball_speed", "carry_distance"])  # pruned, fast
load_shots(sources=["blackmore_trackman_10169"])  # one source
load_shots(canonical_units=False)  # keep native mph/deg/rpm
```

Every frame carries `source_id`, `monitor`, `club`, and
`observation_kind="shot"`. The `apex_native` column is passed through
unconverted because its unit varies by source. For ad hoc SQL, DuckDB reads
the same dataset directly:

```sql
SELECT source_id, count(*) AS shots, avg(ball_speed_mph) AS avg_ball_mph
FROM read_parquet('private_data/launch-monitor-authority/data/authority/database/shot_corpus_parquet/*/*.parquet', hive_partitioning=true)
GROUP BY source_id ORDER BY shots DESC;
```

## Privacy boundary

- No real source rows or generated databases are tracked here.
- Public CI does not receive a private-repository token.
- Small synthetic parser fixtures may live in public consumer repositories.
- The 10,169-shot TrackMan corpus has no trustworthy player identifier and
  must not be presented as within-player evidence.
- Private storage does not change third-party licenses or grant redistribution
  rights.

See `docs/PRIVATE_ACCESS.md` for the folder contract.
