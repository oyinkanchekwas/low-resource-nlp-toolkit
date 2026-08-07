# Version 0.3.0

Version 0.3.0 adds selective language routing and the first measured benchmark for the package.

## Selective routing

`LexicalLanguageRouter.route_selectively` accepts minimum confidence and score-margin thresholds. When a route falls below either threshold, the result retains the original scores and evidence but leaves the accepted language empty and records why it abstained.

The command-line interface exposes the same controls:

```bash
low-resource-nlp route "check" --min-score-margin 0.75
```

`selective_classification_report` separates coverage from accuracy on accepted items and reports the breakdown for each label.

## AfriSenti benchmark

The benchmark uses the official AfriSenti development and test files for Hausa, Igbo, Nigerian Pidgin, Swahili and Yoruba. Dataset paths, the source revision and SHA-256 hashes are recorded in `benchmarks/afrisenti/manifest.json`.

The selected rejection policy was fitted on 8,342 development examples and then applied unchanged to 18,402 test examples. Test coverage was 74.03%, with 89.65% accuracy among accepted routes. Ordinary routing accuracy was 74.75%.

The paired orthography test found that removing diacritics reduced overall test accuracy to 69.87%. The change was concentrated in Yoruba and Igbo, supporting the package default of preserving diacritics.

Full results and caveats are in the [benchmark report](benchmark.md).

## Reproduction

```bash
make benchmark
```

The command downloads and verifies the pinned source files, then writes aggregate JSON and Markdown reports. AfriSenti tweets are not included in the package or repository.
