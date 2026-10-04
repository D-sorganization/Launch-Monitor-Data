# Contributing

Do not submit real launch-monitor rows, screenshots containing player data, or
generated databases to this public repository. Data-source proposals should be
submitted privately to the maintainers with a stable URL, immutable version,
SHA-256, rights status, monitor identity evidence, field inventory, row count,
and limitations.

Public code changes must include synthetic tests and preserve the fail-closed
private checkout contract.

## Merging

Pull requests merge through the GitHub merge queue. Arm auto-merge (squash) and the
queue rebuilds the PR on the latest `main`, runs the required checks once more, and
merges it. There is no need to update a PR branch by hand before merging.
