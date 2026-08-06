# UpstreamDrift Integration

UpstreamDrift's launch-monitor package was introduced in PR
[#8343](https://github.com/D-sorganization/UpstreamDrift/pull/8343). Its
canonical contract uses:

- `m/s` for club and ball speed;
- `m` for distances and height;
- `rad` for angles;
- `rad/s` for spin;
- `s` for time; and
- `1` for ratios such as smash factor.

`database/upstreamdrift_aggregate_metrics.csv` uses the same metric identifiers
and canonical units. It should be loaded as an aggregate reference table—not by
`import_session`, whose `ImportedSession` contract represents shot-level rows.

Recommended integration:

```python
import pandas as pd

reference = pd.read_csv(
    "database/upstreamdrift_aggregate_metrics.csv"
)
driver_speed = reference.query(
    "club == 'Driver' and metric == 'ball_speed'"
)
```

For model evaluation, compare an UpstreamDrift simulation's group summary to
`canonical_mean` and retain `source_id`, `monitor_model`, `club`,
`sample_count`, and `canonical_sd` in the result. Do not feed long-form metric
rows to `compare_monitors`, which expects one metric per shot column and at
least three matched shot pairs.

A future integration issue should add an explicit aggregate-reference reader
to UpstreamDrift rather than weakening `ImportedSession` invariants.
