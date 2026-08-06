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
