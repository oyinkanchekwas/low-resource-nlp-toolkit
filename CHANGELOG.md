# Changelog

## 0.4.0.dev2

- Validate evaluation fields and require a non-empty evaluation set.
- Snapshot profile sequences and normalise character evidence using NFC and lowercase.
- Require setuptools 77.0.3 or later for the licence metadata.
- Record the profile-file hash in benchmark reports and include it in reproduction instructions.
- Write new benchmark output to separate directories and reject existing output files.

## 0.4.0.dev1

- Require language profiles for message-level and word-level routing.
- Add a JSON profile loader with configuration validation.
- Remove the ASCII-only English score adjustment.
- Remove the fixed emotion-category list and automatic label coordinates.
- Add mechanical routing examples and migration guidance.
- Keep earlier benchmark results associated with version 0.3.0.

## 0.4.0 (Unreleased)

- Keep emotion categories distinct unless a caller defines an alias mapping.
- Accept dimensional ratings with a declared scale, source, and annotation perspective.
- Validate finite rating values against the declared scale.

## 0.3.1 (Unreleased)

- Exclude links and usernames from message-level and word-level matching.
- Reject non-finite score-margin thresholds and non-boolean acceptance values.
- Return undefined selective metrics and intervals when their denominators are zero.
- Include benchmark files in the source distribution.

## 0.3.0 - 2026-08-07

### Added

- Selective language routing with configurable confidence and score-margin thresholds.
- Coverage-aware evaluation for systems that can reject uncertain predictions.
- A reproducible AfriSenti benchmark covering Hausa, Igbo, Nigerian Pidgin, Swahili and Yoruba.
- A paired stress test that measures how diacritic removal changes routing results.
- Input manifests, file hashes, aggregate JSON results and statistical intervals for the benchmark.

### Changed

- The route command now reports the score margin, acceptance decision and reason for abstention.
- Version checks now include `CITATION.cff` as well as the package metadata and source version.

## 0.2.1 - 2026-08-07

### Changed

- Updated the package description shown on PyPI to match the current project scope.
- Corrected the software version in `CITATION.cff`.
- Aligned the README, documentation and package metadata on version `0.2.1`.

## 0.2.0 - 2026-07-01

### Added

- Word-level code-switching analysis for short multilingual text, with language assignments, character positions, spans, language counts, and warnings.
- `low-resource-nlp audit` CLI command for evidence-first corpus triage.
- Technical scope notes that explain where the toolkit fits alongside broader African NLP and language-identification work.

### Design Notes

- Word-level classifications support the study of language changes within a message. Confidence and margin thresholds leave weak matches unassigned.
- The package's small dependency footprint supports research and teaching in constrained environments.

## 0.1.0 - 2026-07-01

### Added

- Deterministic text normalisation and tokenisation for noisy multilingual text.
- Lexical language routing for Yoruba, Igbo, Hausa, Nigerian Pidgin, Swahili, and English.
- Emotion label harmonisation with canonical labels and valence-arousal mappings.
- Classification evaluation helpers, confusion matrices, and a small CLI.
- Example input records and routing examples that run without model downloads.
- Responsible release templates for model cards and data statements.

### Design Notes

- The first release deliberately avoids shipping private datasets, API-backed features, or bundled model weights.
- The core is dependency-light so researchers can inspect the behaviour before adding heavier model backends.
