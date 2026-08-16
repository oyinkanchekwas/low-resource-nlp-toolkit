# AfriSenti Routing Benchmark

This benchmark measures corpus-language routing on the AfriSenti development and test sets for Hausa, Igbo, Nigerian Pidgin, Swahili and Yoruba. The router is dependency-light and uses inspectable lexical, character and script evidence.

## Data

- Dataset: [AfriSenti-SemEval 2023 Subtask A](https://github.com/afrisenti-semeval/afrisent-semeval-2023)
- Source revision: `5aec3cfcf87b`
- Licence: CC BY 4.0
- Task paper: [SemEval-2023 Task 12](https://aclanthology.org/2023.semeval-1.315/)
- Source tweets are downloaded locally and hash-checked. They are not committed here.

## Policy selection

The confidence and score-margin thresholds were selected on development data. The search maximised coverage among policies reaching 90.00% selective accuracy.

| Split | Examples | Baseline accuracy | Coverage | Selective accuracy |
| --- | ---: | ---: | ---: | ---: |
| Development | 8,342 | 77.89% | 75.21% | 90.50% |
| Test | 18,402 | 74.75% | 74.03% | 89.65% |

Selected thresholds: confidence >= 0.00; score margin >= 0.75.

## Orthography stress test

Each test tweet was routed again after removing diacritics. This paired test isolates the effect of a common normalisation choice while keeping the text and corpus label fixed.

| Language | Examples | Original accuracy | Diacritics removed | Difference | Route flips |
| --- | ---: | ---: | ---: | ---: | ---: |
| hau | 5,303 | 64.19% | 64.23% | 0.04% | 0.09% |
| ibo | 3,682 | 65.89% | 59.94% | -5.95% | 8.72% |
| pcm | 4,154 | 71.69% | 71.79% | 0.10% | 0.12% |
| swa | 748 | 82.62% | 82.62% | 0.00% | 0.00% |
| yor | 4,515 | 95.90% | 80.73% | -15.17% | 15.17% |

Across all test examples, accuracy changed from 74.75% to 69.87%. The paired difference was -4.88%, with a 95% interval of -5.20% to -4.56%.

## Interpreting the results

The selected policy trades coverage for fewer accepted errors. Its score margin is a ranking gap, not a calibrated probability. The held-out result is therefore a measurement of this fixed router on this corpus, not a general accuracy guarantee.

AfriSenti assigns each tweet to a source-language corpus and includes code-mixed text. It does not provide word-level language labels. An English route inside a Hausa or Nigerian Pidgin subset may reflect code-mixing, so it is not automatically a word-level routing error.

## Reproduce

```bash
PYTHONPATH=src python3 benchmarks/afrisenti/run_benchmark.py --download
```

The JSON report contains confidence intervals, per-language coverage and confusion matrices.
