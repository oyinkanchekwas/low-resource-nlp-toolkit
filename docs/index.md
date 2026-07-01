# Low-Resource NLP Toolkit

This toolkit provides a small, inspectable base layer for low-resource and multilingual NLP experiments. The initial scope is African-language-focused text preparation, language routing, emotion label harmonisation, and transparent evaluation.

## Current Public Scope

- Normalise noisy multilingual text while preserving linguistically meaningful marks.
- Route short text to lightweight language profiles without model downloads.
- Audit code-switched text with token routes, spans, warnings, and abstentions.
- Harmonise emotion labels across categorical and valence-arousal formats.
- Produce compact evaluation reports for classification and routing experiments.
- Document responsible release decisions through model cards and data statements.

## Code-Switch Audit

The audit command is the project's most distinctive current feature. It is meant for corpus triage: seeing which language signals appear in a short text, where a route is weak, and whether the text should be treated as mixed rather than forced into one label.

```bash
low-resource-nlp audit "abeg make una check this model output"
```

The output includes token offsets, accepted language spans, a language mix, a code-switch ratio, and warnings such as `mixed_language_signals` or `ambiguous_or_weak_token_routes`.

## What This Project Is Not

This is not an identity detector, clinical assessment tool, or claim that short text can determine a speaker's language community. The routing module is a research utility for experiment scaffolding and should be evaluated against task-specific data.

## Local Checks

```bash
make check
```

The checks run a repository quality gate and the full unit test suite.

## Release Direction

The package remains dependency-light by design. Benchmark fixtures, Hugging Face examples, and optional model backends belong in future releases only when their provenance and limitations are documented properly.

## Positioning

The project does not claim to beat high-coverage African language identification models. Its current value is a transparent audit layer for low-resource text preparation. See [Novelty Review](novelty_review.md).

## Release Records

- [Version 0.2.0 Release Record](release_plan_v0_2.md)
- [Version 0.1.0 Release Record](release_plan_v0_1.md)
