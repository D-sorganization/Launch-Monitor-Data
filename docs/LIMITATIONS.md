# Limitations and Missing-Data Register

## Current Evidence Limits

- The only redistributable cross-vendor comparison in v0.1 has one participant,
  one TrackMan 4, one Mevo+, indoor use, three clubs, and normalized sea-level
  conditions.
- Published tables provide group aggregates. Raw paired shots are unavailable,
  so nonlinear residual structure and shot-level Bland-Altman analyses cannot
  be reproduced here.
- Retention required complete variables and non-estimated spin from both
  devices. The retained sample can therefore differ systematically from normal
  practice sessions.
- Manual alignment is a confounder. The paper notes that a one-degree alignment
  error can produce about four yards of lateral difference at 250 yards.
- Vendor firmware and algorithms change. A model name without firmware and
  software version is insufficient for a time-stable performance claim.
- Carry and total distance are conditional on environment, normalization, ball,
  landing surface, and vendor flight/roll assumptions.

## Missing Data

| Need | Current State | Consequence |
| --- | --- | --- |
| Licensed TrackMan shot-level corpus | Public 10,169-shot file has no license | Indexed but excluded |
| Licensed Foresight shot-level corpus | No reusable corpus located | Field catalog only |
| Licensed FlightScope shot-level corpus | One unlicensed example plus aggregate study | No shot-level training |
| Three-way simultaneous comparison | Not located | Pairwise vendor conclusions only |
| Outdoor full-flight matched data | Not located under reusable terms | Indoor algorithm effects unresolved |
| Robot-controlled launch matrix | Not located under reusable terms | Swing variability remains confounded |
| Firmware/version-stratified repeats | Sparse | Algorithm drift cannot be quantified |
| Raw trajectory time series | Described in research but no reusable download located | Flight-shape model validation limited |

## Interpretation Rule

Treat vendor differences as observed system-level differences under the stated
protocol. Do not attribute a difference uniquely to a proprietary predictive
model unless measurement, environmental normalization, alignment, filtering,
and roll modeling have been independently separated.
