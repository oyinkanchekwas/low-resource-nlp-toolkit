# Low-Resource NLP Toolkit

The toolkit provides a compact set of Python utilities for multilingual NLP experiments. It was built around recurring problems in African-language text work: preserving orthography, checking mixed-language data, reconciling emotion labels and evaluating systems that can abstain.

## Installation

```bash
python -m pip install low-resource-nlp-toolkit
```

## Language routing

The default router covers Yoruba, Igbo, Hausa, Nigerian Pidgin, Swahili and English. It scores lexical, character and script evidence and returns the evidence behind each route.

```bash
low-resource-nlp route "Ẹ káàrọ̀, báwo ni?"
```

Short or mixed text can leave several routes close together. Set a minimum score margin to reject those cases:

```bash
low-resource-nlp route "check" --min-score-margin 0.75
```

The same operation is available in Python through `LexicalLanguageRouter.route_selectively`.

## Code-switch audits

```bash
low-resource-nlp audit "abeg make una check this model output"
```

An audit records each token's character offsets, proposed route, evidence and score margin. It also groups accepted tokens into spans and reports warnings when the language evidence is mixed or weak.

## Benchmark

The [AfriSenti routing benchmark](benchmark.md) uses pinned development and test data for five languages. The report includes ordinary routing accuracy, coverage and accuracy under rejection, per-language results, confidence intervals and a paired diacritic-removal stress test.

```bash
make benchmark
```

The data is downloaded from the official AfriSenti repository and verified against hashes in the benchmark manifest. Only aggregate results are committed here.

## Other modules

- `normalisation` cleans noisy text while retaining linguistically meaningful marks.
- `labels` maps common emotion names to a canonical set and valence-arousal coordinates.
- `evaluation` produces classification and selective-routing reports.
- `datasets` reads simple CSV and JSONL experiment files.

## Boundaries

The package does not contain private datasets, model weights or API-backed features. Routing results describe evidence in a text sample; they do not establish a speaker's identity or language community. See [Technical Scope](scope.md) for further detail.

## Releases

- [Version 0.3.0](release_notes_v0_3.md)
- [Version 0.2.1](release_notes_v0_2_1.md)
- [Version 0.2.0](release_notes_v0_2.md)
- [Version 0.1.0](release_notes_v0_1.md)
