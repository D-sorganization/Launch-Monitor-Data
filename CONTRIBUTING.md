# Contributing Data

Contributions are welcome when they preserve consent, licensing, and the native
export. Open a data-source issue before a large upload.

## Required Submission Information

- manufacturer and exact monitor model;
- firmware and software/app version when known;
- native export file plus its SHA-256;
- indoor/outdoor setting, measured flight length, altitude, temperature,
  pressure, wind, turf/mat, ball make/model, metallic-dot or RCT-ball use;
- whether values were normalized and the exact vendor settings;
- units and handedness/sign conventions;
- which fields the device labeled measured, estimated, or calculated;
- license or an explicit contributor statement permitting redistribution;
- confirmation that player names, email addresses, account IDs, facility
  identifiers, and other personal data have been removed or knowingly licensed.

Do not submit files obtained by scraping a private portal or bypassing access
controls. Do not submit another person's session without permission.

## Review Gates

1. Preserve the original file in a source-specific staging branch.
2. Register provenance and rights in `data/source_catalog.csv`.
3. Add a parser fixture containing only consented or synthetic representative
   rows.
4. Map native headers to the canonical contract without deleting native fields.
5. Add tests for units, signs, missing values, and measured/estimated status.
6. Run `launch-monitor-data validate`, rebuild, and run `python -m pytest`.
7. A maintainer verifies licensing before any observation is marked
   `redistributable`.

Raw data and canonical data must remain separable. Never silently resolve
conflicting units or infer a monitor model.
