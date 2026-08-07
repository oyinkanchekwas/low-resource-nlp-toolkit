# Changelog

All notable changes to this project are recorded here. The format is deliberately plain so release decisions remain easy to audit.

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

- Code-switch audit reports for short multilingual text, including token routes, character offsets, accepted spans, language-mix counts, and warnings.
- `low-resource-nlp audit` CLI command for evidence-first corpus triage.
- Technical scope notes that explain where the toolkit fits alongside broader African NLP and language-identification work.

### Design Notes

- The audit layer complements high-coverage model-based language identification. It favours inspectable evidence and abstention on weak token routes.
- The package remains dependency-light so the audit can run in constrained research and teaching environments.

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
