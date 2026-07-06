# Version 0.2.0 Release Notes

Version 0.2.0 adds evidence-first code-switch auditing for short, noisy, mixed-language text.

## Included

- `audit_code_switching` Python API.
- `low-resource-nlp audit` CLI command.
- Token-level language routes with original character offsets.
- Accepted language spans for mixed text.
- Language-mix counts and code-switch ratio.
- Warnings for weak evidence, ambiguity, low supported-language coverage, and high code-switching.
- Scope notes explaining how the toolkit fits alongside broader African NLP and language-identification work.

## Published Artefacts

- [GitHub release](https://github.com/oyinkanchekwas/low-resource-nlp-toolkit/releases/tag/v0.2.0)
- [PyPI package](https://pypi.org/project/low-resource-nlp-toolkit/0.2.0/)
- [TestPyPI package](https://test.pypi.org/project/low-resource-nlp-toolkit/0.2.0/)

## Scope

This release is not a state-of-the-art African language identifier, a broad language-coverage system, a gold-standard annotation tool, or a substitute for native-speaker review and task-specific evaluation. Routing output should not be treated as identity, ethnicity, nationality, or language-community inference.
