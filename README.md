# Low-Resource NLP Toolkit

Python tools for preparing and evaluating multilingual text, with an initial focus on African languages. The package covers Unicode-aware normalisation, lightweight language routing, code-switch audits, emotion-label mapping and classification metrics.

Current release: `0.3.0`.

**[Install from PyPI](https://pypi.org/project/low-resource-nlp-toolkit/)**

```bash
pip install low-resource-nlp-toolkit
```

## What it covers

- Text normalisation that preserves diacritics by default.
- Lexical routing for Yoruba, Igbo, Hausa, Nigerian Pidgin, Swahili and English.
- Selective routing, so weak decisions can be rejected and left unassigned.
- Token-level code-switch audits with evidence spans and character offsets.
- Emotion-label harmonisation across categorical and valence-arousal formats.
- Classification, confusion-matrix and coverage-aware evaluation.
- A command-line interface with no model download or API key requirement.

## Measured benchmark

The router has been evaluated on the official AfriSenti development and test splits for Hausa, Igbo, Nigerian Pidgin, Swahili and Yoruba. The source revision and file hashes are pinned, and the source tweets remain outside this repository.

On 18,402 held-out test tweets, ordinary corpus-language routing accuracy was 74.75%. A rejection threshold chosen on development data reached 89.65% accuracy on the accepted test items at 74.03% coverage.

A paired stress test also measured the effect of removing diacritics. Overall accuracy fell from 74.75% to 69.87%; the largest changes were for Yoruba, down 15.17 percentage points, and Igbo, down 5.95 points. This is why the normaliser preserves diacritics unless removal is requested explicitly.

See the [full benchmark report](https://oyinkanchekwas.github.io/low-resource-nlp-toolkit/benchmark/) for the method, per-language results, confidence intervals and limitations.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install low-resource-nlp-toolkit
low-resource-nlp --version
```

Route a text sample:

```bash
low-resource-nlp route "abeg make una help me check this model output"
```

Reject routes with a narrow score margin:

```bash
low-resource-nlp route "check" --min-score-margin 0.75
```

Audit code-switched language evidence:

```bash
low-resource-nlp audit "abeg make una check this model output"
```

Normalise text:

```bash
low-resource-nlp normalise "Ẹ káàrọ̀!!! Visit https://example.com @user"
```

Map an emotion label:

```bash
low-resource-nlp label joy
```

## Python API

```python
from low_resource_nlp import (
    LexicalLanguageRouter,
    audit_code_switching,
    label_to_valence_arousal,
    normalise_text,
)

text = normalise_text("Ẹ káàrọ̀, báwo ni?")
router = LexicalLanguageRouter.default()
route = router.route_selectively(text, min_score_margin=0.75)
audit = audit_code_switching("abeg make una check this model output")
emotion = label_to_valence_arousal("joy")

print(route.accepted_language_code, route.score_margin)
print(audit.language_mix, audit.warnings)
print(emotion)
```

## Reproducing the benchmark

```bash
git clone https://github.com/oyinkanchekwas/low-resource-nlp-toolkit.git
cd low-resource-nlp-toolkit
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
make benchmark
```

The command downloads the ten pinned AfriSenti files, verifies their SHA-256 hashes, selects the rejection policy on development data and writes aggregate test results. It does not copy source tweets into the report.

Run the local checks with:

```bash
make check
```

## Limitations

The router uses small, inspectable lexical profiles. It is useful for corpus checks, teaching, small experiments and reproducible baselines. Trained language-identification models and native-speaker review are still needed for broader coverage. AfriSenti provides corpus-level language labels and includes code-mixed text, so an apparent routing error is not always an incorrect word-level decision.

Language and emotion predictions must not be treated as identity labels or clinical assessments.

## Links

- [Documentation](https://oyinkanchekwas.github.io/low-resource-nlp-toolkit/)
- [Corpus triage tutorial](https://oyinkanchekwas.github.io/low-resource-nlp-toolkit/tutorial/)
- [Benchmark report](https://oyinkanchekwas.github.io/low-resource-nlp-toolkit/benchmark/)
- [Changelog](https://github.com/oyinkanchekwas/low-resource-nlp-toolkit/blob/main/CHANGELOG.md)
- [Contributing guide](https://github.com/oyinkanchekwas/low-resource-nlp-toolkit/blob/main/CONTRIBUTING.md)
- [Citation metadata](https://github.com/oyinkanchekwas/low-resource-nlp-toolkit/blob/main/CITATION.cff)
