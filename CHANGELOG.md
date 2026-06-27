# Changelog

All notable changes to this project are recorded here. The format is deliberately plain so release decisions remain easy to audit.

## 0.1.0 - Unreleased

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
