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
authority manifest match the lock. A missing checkout, unavailable credential,
or commit mismatch is an error; there is no public-source fallback.
