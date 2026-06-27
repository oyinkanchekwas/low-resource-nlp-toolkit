# Low-Resource NLP Toolkit

This toolkit provides a small, inspectable base layer for low-resource and multilingual NLP experiments. The initial scope is African-language-focused text preparation, language routing, emotion label harmonisation, and transparent evaluation.

## Current Public Scope

- Normalise noisy multilingual text while preserving linguistically meaningful marks.
- Route short text to lightweight language profiles without model downloads.
- Harmonise emotion labels across categorical and valence-arousal formats.
- Produce compact evaluation reports for classification and routing experiments.
- Document responsible release decisions through model cards and data statements.

## What This Project Is Not

This is not an identity detector, clinical assessment tool, or claim that short text can determine a speaker's language community. The routing module is a research utility for experiment scaffolding and should be evaluated against task-specific data.

## Local Checks

```bash
make check
```

The checks run a repository quality gate and the full unit test suite.

## Release Direction

The first public release is intended to be useful as a dependency-light research package. Benchmark fixtures, Hugging Face examples, and optional model backends should be added only when their provenance and limitations can be documented properly.
