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
commit `78f0a42540e523ac883d843394b30a636311bf9d` recorded in
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
```

The API verifies the exact private commit, qualification schemas, policy/count
agreement, and SHA-256 hashes before returning aggregate or source/metric policy
metadata. It never returns shot rows. Unknown vendors, unknown operations,
missing metadata, commit drift, and hash drift fail closed. Current metadata
does not authorize within-player, longitudinal, strokes-gained, same-shot
cross-device, public-output, or vendor-surrogate training workflows. ShotLink
remains prohibited for vendor training and public output.

## Working with the shot corpus

The private authority carries a source-partitioned Parquet corpus
(261,666 shots across 27 sources at the pinned Release A commit). With the `corpus` extra
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
