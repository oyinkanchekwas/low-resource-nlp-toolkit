# Novelty Review

This note records the project's current novelty claim and its limits.

## Honest Assessment

The toolkit is not novel as a broad African language identification model. That space already has stronger model-based work:

- AfroLID introduced neural language identification for 517 African languages and varieties, with broad multi-domain coverage.
- AfroScope, a 2026 preprint, extends the direction further with data and models for 713 African languages and a hierarchical approach for confusable languages.
- Masakhane has already shown how community-led African NLP can produce public translation resources, benchmarks, and research infrastructure.
- AfriSenti provides a sentiment benchmark for 14 African languages and shows the value of native-speaker-labelled data.

The toolkit is also not novel as a general normalisation, metric, or label-mapping library. Those are useful support functions, but they do not make the project distinctive on their own.

## Useful Gap

The more defensible contribution is an evidence-first audit layer for noisy, short, code-switched low-resource text.

Many strong systems optimise for prediction quality. Early-stage researchers and community projects often need a different first step: inspect a small corpus, see which tokens triggered a route, identify mixed-language spans, and decide where the tool should abstain. That is especially useful before collecting more data, choosing a model backend, or publishing a benchmark.

The `audit` module adds that layer:

- token-level routes with original character offsets;
- accepted language spans for mixed text;
- language-mix counts and code-switch ratio;
- warnings for weak evidence, ambiguity, low coverage, and high code-switching;
- JSON output from both Python and the CLI;
- no model download, API call, or private dataset dependency.

## Novelty Claim

A safe way to describe the project is:

> This is a dependency-light research toolkit for inspecting low-resource African-language text before heavier modelling. Its distinctive contribution is an evidence-first code-switch audit that exposes token-level routing evidence, abstains on weak signals, and produces structured reports for corpus triage.

## References for Positioning

- AfroLID: `https://arxiv.org/abs/2210.11744`
- AfroScope: `https://arxiv.org/abs/2601.13346`
- Masakhane: `https://arxiv.org/abs/2003.11529`
- AfriSenti: `https://arxiv.org/abs/2302.08956`
- Code-Switched Language Identification is Harder Than You Think: `https://arxiv.org/abs/2402.01505`
