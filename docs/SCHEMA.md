# Database Schema

## `sources`

One row per source. `redistribution_status` is either `redistributable` or
`reference_only`. `sha256` identifies an external byte stream when one was
downloaded for verification.

## `vendor_fields`

One row per vendor/model/metric claim. `availability` distinguishes standard,
paid package, add-on, documented, observed-in-example, and unresolved profile
coverage. `measurement_claim` is intentionally source language—not an
independent accuracy judgment.

## `study_comparisons`

One row per club and metric from the matched TrackMan 4/Mevo+ paper. It retains
reported units and the published means, standard deviations, ranges, mean
difference, MAPE, ICCs, and Pearson correlation.

`mean_difference_trackman_minus_flightscope` follows the paper's table order.
This sign must not be flipped without changing the column name and schema
version.

## `metric_observations`

Two long-form rows are generated from every comparison row—one per monitor.
Reported values are retained and SI canonical values are added. These are
aggregate observations with `aggregation_level=group_mean` and
`matched_shots=1`.

Additional rows come from `data/studies/aggregate_observations.csv`, an
optional input for redistributable single-monitor group statistics. Each row
records monitor vendor and model, software version, environment, cohort,
club, metric, reported unit, sample count, measurement status, and a
matched-shots flag. Validation fails closed when a row references a source
that is unknown or not redistributable, uses an unknown metric or a unit that
cannot be converted, or contains non-finite means or negative standard
deviations.

The `cohort` column names the participant group an aggregate summarizes
(for example `professional` versus `amateur`). Rows derived from the paired
comparison study use `single_participant`. `reported_sd` and `canonical_sd`
are null when a source publishes mean-only tables.

The canonical metric vocabulary is a deliberate compatibility contract with
UpstreamDrift. It is not a claim that differently named vendor metrics are
physically identical in every implementation.
