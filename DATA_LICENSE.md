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
