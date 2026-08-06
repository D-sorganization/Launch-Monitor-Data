"""Explicitly fetch hash-pinned public files that lack redistribution rights."""

from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

URL = (
    "https://raw.githubusercontent.com/tim-blackmore/"
    "launch-monitor-regression/main/data.csv"
)
EXPECTED_SHA256 = "fae80d325e69c928debcbbbacd908c1e4a8b0d44d5cd5290a2bbad95b83cae04"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--accept-no-license",
        action="store_true",
        help="Acknowledge that the external file has no stated reuse license",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("external/reference_only/blackmore_trackman_data.csv"),
    )
    args = parser.parse_args()
    if not args.accept_no_license:
        parser.error("--accept-no-license is required; the file is not open data")

    request = urllib.request.Request(URL, headers={"User-Agent": "launch-monitor-data"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != EXPECTED_SHA256:
        raise ValueError(
            f"External file changed: expected {EXPECTED_SHA256}, received {actual}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"Fetched {len(payload)} bytes to {args.output} (reference only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
