# Changelog

All notable changes to this project are recorded here. The format is deliberately plain so release decisions remain easy to audit.

## 0.2.0 - 2026-07-01

### Added

- Code-switch audit reports for short multilingual text, including token routes, character offsets, accepted spans, language-mix counts, and warnings.
- `low-resource-nlp audit` CLI command for evidence-first corpus triage.
- Documentation that positions the toolkit against existing African NLP and language-identification work without claiming broad model novelty.

### Design Notes

- The audit layer is meant to complement high-coverage model-based language identification. It favours inspectable evidence and abstention on weak token routes.
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
- Public benchmark work is kept separate from the core package until dataset provenance and documentation are ready.
