# Private authority access

The canonical private data folder is `data/authority/` in
`D-sorganization/Launch-Monitor-Flight-Model-Campaign`. Public consumers pin an
exact repository commit in `private_data.lock.json` and clone it under the
git-ignored `private_data/` folder.

Set `LAUNCH_MONITOR_DATA_ROOT` to the private repository checkout root. The
Python package then reads catalog inputs from
`data/authority/catalog/data/`. Restricted raw snapshots and the normalized
shot corpus remain under adjacent private-only folders and are never copied to
this public Git tree.

`python scripts/sync_private_data.py check` verifies that the checkout HEAD and
authority manifest match the lock. It also verifies the v2 qualification and
capability schemas plus the SHA-256 hashes for the capability and source/metric
eligibility metadata. A missing checkout, unavailable credential, commit
mismatch, missing qualification file, or metadata hash mismatch is an error;
there is no public-source fallback.

The same check now verifies the private Release B `status.json` schema and the
SHA-256 hashes of its schedule and ledger. Those private CSVs remain inside the
ignored authenticated checkout; the public package exposes only aggregate
progress through `load_release_b_status()`. At the pinned commit the verified
state is 252 planned, 0 triggered, 0 analyzed, and not confirmatory-ready.

`launch_monitor_data.load_capabilities()` exposes aggregate, data-free vendor
capabilities. `load_source_metric_eligibility()` exposes only the traceable
source/metric policy matrix. It uses an explicit field allowlist so a future
private schema cannot accidentally expose shot-level columns through this
public client. `vendor_operation()` supplies boolean permission and fail-closed
reasons for UI clients.

`load_release_b_status()` additionally recomputes schedule membership, 84-pair
cell counts, ledger stage totals, non-overlapping exclusions, readiness, and
vendor-training eligibility before returning a frozen aggregate record. A
schedule is not an observation: the current record reports zero eligible
vendor-training decisions and zero group-safe training rows.

The inventory row count is not a validation sample size. Current eligibility
disables player/session inference, longitudinal and strokes-gained analyses,
same-shot cross-device claims, public row output, and vendor-surrogate training.
ShotLink is explicitly quarantined from training and public output. TrackMan-
comparable model agreement is available for qualified source/metric cohorts,
but the historical neural surrogate is retired because its split was not based
on a trusted repeating player/session group.
