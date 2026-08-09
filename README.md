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

## Privacy boundary

- No real source rows or generated databases are tracked here.
- Public CI does not receive a private-repository token.
- Small synthetic parser fixtures may live in public consumer repositories.
- The 10,169-shot TrackMan corpus has no trustworthy player identifier and
  must not be presented as within-player evidence.
- Private storage does not change third-party licenses or grant redistribution
  rights.

See `docs/PRIVATE_ACCESS.md` for the folder contract.
