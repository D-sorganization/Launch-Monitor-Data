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

The canonical metric vocabulary is a deliberate compatibility contract with
UpstreamDrift. It is not a claim that differently named vendor metrics are
physically identical in every implementation.
