# Implementation Handoff

Keep this file current and concise. Replace instructional placeholders; do not append an unbounded transcript.

## Identity

- Repository: `D-sorganization/Launch-Monitor-Data`
- Working directory: `C:/tmp/wave2/Launch-Monitor-Data`
- Branch: `bot/observation-kind-aggregate-stamp`
- Baseline commit: `08a6c8c18933b132002f38bb6ccc3ce3cbc05f6b`
- Implementation commit: `SELF` — the commit containing this update; resolve with `git rev-parse HEAD`
- Pull request: to be created after commit
- Governing issue/epic: D-sorganization/Launch-Monitor-Data#4 (data-side half; the reader/importer half is tracked in D-sorganization/UpstreamDrift#8365)

## Objective and Status

- Objective: stamp `observation_kind` on every emitted metric observation so the UpstreamDrift aggregate export (`upstreamdrift_aggregate_metrics.csv`) and `metric_observations.csv`/SQLite carry the shot/aggregate discriminator that UpstreamDrift's `flexible_analysis` aggregate guard reads (it currently defaults unmarked rows to `"shot"`).
- Status: complete
- Completed: `_observation_kind` classifier added; `_normalize_observations` and `_normalize_aggregates` stamp the marker; SQLite `metric_observations` gains a `CHECK (observation_kind IN ('shot','aggregate'))` column; `docs/SCHEMA.md` updated (column block + contract prose); three new unit tests pin the contract.
- Remaining: UpstreamDrift-side reader/importer and analytics-UI surfacing (UpstreamDrift#8365); the private authority's next lock bump will regenerate the export with the new column.

## Files and Decisions

- Files changed: `src/launch_monitor_data/build.py` (classifier + stamping + schema), `tests/test_build_normalization.py` (3 TDD tests, written red first), `docs/SCHEMA.md` (kept in lockstep per `test_schema_doc.py`), `AGENT_HANDOFF.md` (created per Repository_Management convention).
- Key decisions: only exact `shot` aggregation level maps to `observation_kind="shot"`; every group statistic (including paired-comparison group means from `study_comparisons`) maps to `"aggregate"`, matching UpstreamDrift's guard semantics (`any(kind.lower() != "shot")`). Column is additive; consumers read it optionally.
- User-owned or unrelated worktree changes: none observed.

## Validation

- `python -m pytest tests -q` — pass, 49 passed.
- `python -m ruff check src tests` — pass.
- SQLite round-trip smoke (`_create_database` with one aggregate row) — `observation_kind='aggregate'` persisted, table columns match `docs/SCHEMA.md`.

## Blockers and Risks

- Blockers: none for this PR. #4's reader/UI acceptance bullets remain owned by UpstreamDrift#8365.
- Risks/assumptions: additive column only; UpstreamDrift reads `observation_kind` as an optional field, so existing consumers tolerate it.

## Next Steps

1. Merge PR and let the quality gate confirm.
2. Land the UpstreamDrift importer (#8365) against this stamped export.

## Change Log

- `SELF` — created handoff file; recorded observation_kind contract decision.