# Data boundary and licensing

This public repository distributes no launch-monitor datasets. Its code is MIT
licensed. Third-party data in the private authority retains its source-specific
rights status; private storage does not relicense it.

Any public release of source rows, named-player values, or row-level derived
artifacts requires a separate provenance, privacy, and rights review.

## Ingested sources recorded with a redistribution license basis

The private authority ingests the following shot-level source under its
publisher-granted redistribution license. The license basis is recorded here so
that any future public release cites it correctly; it does not by itself
authorize a release (see the review gate above).

### CaddieSet (`caddieset_github`)

- **License:** MIT — https://github.com/damilab/CaddieSet/blob/main/LICENSE
- **Repository:** https://github.com/damilab/CaddieSet
- **Byte-pinned commit:** `3c73d9d40580bb8a5a10711ad1fa10735a205ffe`
- **Ingested rows:** 1,757 shots from eight golfers (anonymized numeric
  `GolferId` 1–8; no names or contact data in the redistributed rows)
- **Monitor attribution:** the publisher does not identify the launch monitor;
  the corpus records it honestly as "Unspecified camera-based launch monitor".

The publisher requests the following citation for research use:

```bibtex
@inproceedings{jung2025caddieset,
  title={CaddieSet: A Golf Swing Dataset with Human Joint Features and Ball Information},
  author={Jung, Seunghyeon and Hong, Seoyoung and Jeong, Jiwoo and Jeong, Seungwon and Choi, Jaerim and Kim, Hoki and Lee, Woojin},
  booktitle={Proceedings of the Computer Vision and Pattern Recognition Conference},
  pages={5988--5996},
  year={2025}
}
```

### Suzuki et al. 2021 (`suzuki_2021_trackman`)

- **License:** CC BY 4.0 — The Open Sports Sciences Journal's editorial policy
  licenses open-access articles under the Creative Commons Attribution 4.0
  International Public License (https://creativecommons.org/licenses/by/4.0/).
- **Article:** Suzuki T., Sheahan J.P., Miyazawa T., Okuda I., Ichikawa D.
  "Comparison of TrackMan Data between Professional and Amateur Golfers at
  Swinging to Uphill and Downhill Fairways", Open Sports Sci J 2021; 14:
  137-143. DOI 10.2174/1875399X02114010137.
- **Transcribed rows:** Table 1's group means and SDs — 24 `group_mean`
  observations (six metrics × amateur/professional × uphill/downhill; n=25
  amateur, n=42 professional) — recorded in the private authority's
  `studies/aggregate_observations.csv` and its derived database, with
  attribution carried by this section.

Please cite the article above when reusing the transcribed statistics:
```bibtex
@article{suzuki2021trackman,
  title={Comparison of TrackMan Data between Professional and Amateur Golfers at Swinging to Uphill and Downhill Fairways},
  author={Suzuki, Takeru and Sheahan, John Patrick and Miyazawa, Taiki and Okuda, Isao and Ichikawa, Daisuke},
  journal={The Open Sports Sciences Journal},
  volume={14},
  pages={137--143},
  year={2021},
  doi={10.2174/1875399X02114010137}
}
```

### Robinson et al. 2024 (`robinson_2024_elite_female`)

- **License:** CC BY 4.0 — verified 2026-09-03 from the article page and
  Crossref vor metadata (CC BY 4.0,
  https://creativecommons.org/licenses/by/4.0/).
- **Article:** "Relationships and Within-Group Differences in Physical
  Attributes and Golf Performance in Elite Amateur Female Players", Life
  2024; 14(6):674. DOI 10.3390/life14060674.
- **Transcribed rows:** Table 1's driver shot metrics — club-head speed, ball
  speed, carry distance, and smash factor — 4 `group_mean` observations
  (n=19 elite female amateurs, TrackMan 4, outdoor range, own drivers,
  Titleist ProV1) recorded in the private authority's
  `studies/aggregate_observations.csv` and its derived database, with
  attribution carried by this section.

Please cite the article above when reusing the transcribed statistics:
```bibtex
@article{robinson2024elite,
  title={Relationships and Within-Group Differences in Physical Attributes and Golf Performance in Elite Amateur Female Players},
  journal={Life},
  volume={14},
  number={6},
  pages={674},
  year={2024},
  doi={10.3390/life14060674}
}
```

### Brennan et al. 2024 (`brennan_2024_amateur`)

- **License:** CC BY 4.0 — verified 2026-09-03 via Crossref license metadata
  (vor) (CC BY 4.0, https://creativecommons.org/licenses/by/4.0/).
- **Article:** "Associations and Within-Group Differences in Physical
  Characteristics and Golf Performance Data in High-Level Amateur Players",
  Appl. Sci. 2024; 14(5):1854. DOI 10.3390/app14051854.
- **Transcribed rows:** Table 2's shot metrics — 8 `group_mean` observations
  across Driver and 6-Iron (n=26 high-level amateurs, FlightScope Mevo+,
  indoor range): club-head speed 109.24 +/- 8.43 / 92.92 +/- 7.12 mph,
  ball speed 155.06 +/- 15.29 / 122.01 +/- 10.8 mph, carry distance
  239.15 +/- 31.33 / 169.81 +/- 19.64 yd, and smash factor 1.42 +/- 0.06 /
  1.32 +/- 0.06 (Driver / 6-Iron), recorded in the private authority's
  `studies/aggregate_observations.csv` and its derived database, with
  attribution carried by this section.

Please cite the article above when reusing the transcribed statistics:
```bibtex
@article{brennan2024amateur,
  title={Associations and Within-Group Differences in Physical Characteristics and Golf Performance Data in High-Level Amateur Players},
  journal={Applied Sciences},
  volume={14},
  number={5},
  pages={1854},
  year={2024},
  doi={10.3390/app14051854}
}
```

### Ichikawa et al. 2022 (`ichikawa_2022_x3_variability`)

- **License:** CC BY 4.0 — verified 2026-09-03 via Crossref license metadata
  (CC BY 4.0, https://creativecommons.org/licenses/by/4.0/).
- **Article:** "Relationship Between Variability in Clubhead Movement Using a
  Doppler Radar Launch Monitor and Golf Strokes Across 15 Drives", Int J
  Kinesiol Sports Sci 2022; 10(4):7. DOI 10.7575/aiac.ijkss.v.10n.4p.7.
- **Transcribed rows:** Table 1's clubhead speed across 15 driver shots
  (indoor range, FlightScope X3, own drivers) — 2 `group_mean` observations:
  amateur golfers 41.6 +/- 4.3 m/s, skilled golfers 48.8 +/- 2.2 m/s
  (n=14 each cohort) — recorded
  in the private authority's `studies/aggregate_observations.csv` and its
  derived database, with attribution carried by this section. The article's
  angular variability magnitudes are reported unsigned and are honestly not
  transcribed into signed canonical metrics.

Please cite the article above when reusing the transcribed statistics:
```bibtex
@article{ichikawa2022variability,
  title={Relationship Between Variability in Clubhead Movement Using a Doppler Radar Launch Monitor and Golf Strokes Across 15 Drives},
  journal={International Journal of Kinesiology and Sports Science},
  volume={10},
  number={4},
  pages={7},
  year={2022},
  doi={10.7575/aiac.ijkss.v.10n.4p.7}
}
```

### Navarro 2022 (`appsci_2022_insole_pressure`)

- **License:** CC BY 4.0 — verified via Crossref license metadata (vor) for
  Applied Sciences 12(1):358 (CC BY 4.0,
  https://creativecommons.org/licenses/by/4.0/).
- **Article:** Navarro E., Mancebo J.M., Farazi S., del Olmo M., Luengo D.
  "Foot Insole Pressure Distribution during the Golf Swing in Professionals
  and Amateur Players", Appl. Sci. 2022; 12(1):358.
  DOI 10.3390/app12010358.
- **Transcribed rows:** Table 1's club speeds at impact (Foresight GC2+HMT,
  5 good shots per club, outdoor driving range) — 6 `group_mean` observations
  (Driver and 5-Iron for professional n=15, medium-handicap n=15, and
  high-handicap n=25 cohorts) recorded in the private authority's
  `studies/aggregate_observations.csv` and its derived database, with
  attribution carried by this section. The article's primary insole-pressure
  percentages are not launch-monitor metrics and are not transcribed.

Please cite the article above when reusing the transcribed statistics:
```bibtex
@article{navarro2022insole,
  title={Foot Insole Pressure Distribution during the Golf Swing in Professionals and Amateur Players},
  author={Navarro, Enrique and Mancebo, Juan M. and Farazi, Sadegh and del Olmo, Miguel and Luengo, David},
  journal={Applied Sciences},
  volume={12},
  number={1},
  pages={358},
  year={2022},
  doi={10.3390/app12010358}
}
```
