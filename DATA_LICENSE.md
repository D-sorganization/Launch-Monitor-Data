# Data License and Attribution

## Redistributable Data

The normalized rows derived from Bliss and Langdown (2026) are licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), matching the source:

> Bliss, A. and Langdown, B. L. (2026). Comparing indoor tracking of golf ball
> and club metrics: Consistency and absolute agreement of the FlightScope Mevo+
> and TrackMan 4 launch monitors. *JSAMS Plus*, 7, 100128.
> <https://doi.org/10.1016/j.jsampl.2025.100128>

The source catalog also identifies Suzuki et al. (2021) as CC BY 4.0. Its
statistics are registered for future extraction but are not included in the
current observation table.

To the extent D-sorganization holds database rights in the compilation,
`data/`, `database/*.csv`, and `database/*.sqlite` are offered under CC BY 4.0,
subject to each row's source-specific rights and the exceptions below.

## Reference-Only Entries

Rows marked `reference_only` are citations and factual metadata. Referenced
external files are not redistributed. In particular:

- `blackmore_trackman_10169` is public and hash-pinned but has no stated
  license;
- `leach_2017_validation` is CC BY-NC-ND 4.0;
- `shaw_2023_reliability` is marked In Copyright;
- public gists and sample-export sites without explicit reuse terms are not
  treated as open data;
- the public shot-level GitHub datasets cataloged in 2026 (TrackMan, Mevo+,
  Garmin R10/R50, SkyTrak, Rapsodo MLM2PRO, Square Golf, Awesome Golf, and
  others) are hash- or commit-pinned but have no stated licenses, and several
  contain player names, so they are indexed only;
- `caddieset_github` carries a verified MIT license and `openflight_session_log`
  a verified AGPL-3.0-or-later license; both stay reference-only because MIT
  shot-level ingestion needs a schema extension and AGPL copyleft is
  incompatible with this project's CC BY redistribution;
- vendor documentation pages and open-access studies cataloged from
  search-index snapshots in 2026 record their expected licenses but remain
  reference-only until the pages are verified directly.

## Published Reference Values

The `published_references` table compiles individual factual values (tour
averages, benchmark scores, and player launch numbers) from publicly
published sources, each row citing the publications it was taken from. These
are quotations of facts, not reproductions of any publication's expression,
layout, or complete dataset presentation. TrackMan is a trademark of TrackMan
A/S; the compiled values are attributed to their publishers and this project
claims no endorsement by, or affiliation with, TrackMan or any publisher.
Player names appear only as already published by the cited press sources.
Users who republish this table should preserve the per-row citations.

Users who independently obtain those files are responsible for complying with
their terms. Nothing here relicenses third-party content.
