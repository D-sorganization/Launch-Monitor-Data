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
commit recorded in `private_data.lock.json`. It does not accept a moving branch
or silently download from third-party sources. Git ignores the checkout.

Users without private access can inspect and test the public code, but data
commands fail closed until an authorized checkout is present.

## Working with the shot corpus

The private authority carries a source-partitioned Parquet corpus
(261,666 shots across 27 sources as of 2026-08-18). With the `corpus` extra
installed (`pip install -e ".[corpus]"`), load it as an analysis-ready frame
in the canonical SI contract shared with UpstreamDrift's `launch_monitor`
analytics (angles in radians, speeds in m/s, spin in rad/s, distances in m):

```python
from launch_monitor_data.corpus import available_sources, load_shots

load_shots(metrics=["ball_speed", "carry_distance"])   # pruned, fast
load_shots(sources=["blackmore_trackman_10169"])       # one source
load_shots(canonical_units=False)                      # keep native mph/deg/rpm
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
