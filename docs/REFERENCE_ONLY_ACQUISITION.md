# Reference-Only Acquisition

The Blackmore TrackMan file is valuable—10,169 shot rows and 35 metrics—but its
repository has no license. It is therefore excluded from committed data.

Researchers who independently determine that their use is permitted can fetch
the exact verified bytes into an ignored directory:

```powershell
python scripts/fetch_reference_only.py --accept-no-license
```

The script refuses to run without the acknowledgement and rejects any payload
whose SHA-256 differs from the catalog. Fetching the file does not grant rights
to redistribute it or model outputs that reproduce protected expression.

## Full Local Shot Corpus

The same posture scaled to every shot-level GitHub source in the catalog:

```powershell
python scripts/build_shot_corpus.py
```

The builder clones each pinned repository at its exact pinned commit,
verifies byte-level SHA-256 where the catalog records one, parses the native
exports (TrackMan stacked and normalized formats, FlightScope, Garmin Golf
app, SkyTrak, Rapsodo MLM2PRO, Square Golf, Awesome Golf, CaddieSet, and
OpenFlight), and writes a unified `local_data/shot_corpus.sqlite` of roughly
23,000 shots. `local_data/` is git-ignored: the corpus is reproduced on
demand from the original hosts and is never committed or redistributed.
Player-identifying columns are replaced with stable per-source labels before
storage. Extracted numeric columns are convenience values in source-native
units; the `native_json` column preserves each row verbatim (minus personal
data) and is the ground truth.

Because this repository is public, the corpus must stay out of version
control until each source carries a license permitting redistribution. If
the repository is ever made private for internal analysis, committing the
corpus becomes an owner decision rather than a policy violation, but the
per-source license metadata in the catalog remains authoritative either way.
