# Version 0.2.0 Release Record

The 0.2.0 release adds an evidence-first code-switch audit. It gives researchers a lightweight way to inspect short, noisy, mixed-language text before choosing heavier models or publishing a dataset.

## Release Contents

- `audit_code_switching` Python API.
- `low-resource-nlp audit` CLI command.
- Token-level routes with original character offsets.
- Accepted language spans for mixed text.
- Language-mix counts and code-switch ratio.
- Warnings for weak evidence, ambiguity, low supported-language coverage, and high code-switching.
- Scope notes that explain where the package fits alongside broader African NLP and language-identification work.

## Not in Scope

- State-of-the-art African language identification.
- Broad language coverage beyond the current lightweight profiles.
- Identity, ethnicity, nationality, or language-community inference.
- Gold-standard sentiment or emotion annotation.
- Replacement for native-speaker review or task-specific evaluation.

## Completed Checks

- `make check` passed locally.
- `git diff --check` passed locally.
- Local source and wheel builds passed.
- `twine check` passed for the 0.2.0 wheel and source distribution.
- Fresh local wheel install passed.
- GitHub Actions passed on Python 3.9, 3.10, and 3.11.
- TestPyPI trusted publishing succeeded for `0.2.0`.
- A fresh install from TestPyPI passed, including CLI and import smoke tests.
- GitHub release `v0.2.0` was created with the wheel and source distribution.
- PyPI trusted publishing succeeded for `0.2.0`.
- A fresh install from PyPI passed, including CLI and import smoke tests.

## Release Evidence

- Commit: `f9ce7f91d95abddc39676bffe9032fb53f016936`
- GitHub release: `https://github.com/oyinkanchekwas/low-resource-nlp-toolkit/releases/tag/v0.2.0`
- TestPyPI release: `https://test.pypi.org/project/low-resource-nlp-toolkit/0.2.0/`
- PyPI release: `https://pypi.org/project/low-resource-nlp-toolkit/0.2.0/`
- GitHub Actions tests run: `28539467717`
- TestPyPI publish run: `28539500134`
- PyPI publish run: `28539670508`

## Release Summary

The release turns the project from a small low-resource NLP helper into an installable package that can audit code-switched text, show the evidence behind language-routing decisions, and abstain when token-level signals are weak.
