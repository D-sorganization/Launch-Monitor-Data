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
