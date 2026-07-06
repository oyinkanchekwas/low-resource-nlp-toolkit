# Contributing

This project is early-stage, but the contribution bar is intentionally practical: changes should make low-resource NLP work easier to inspect, reproduce, or document.

## Contribution Areas

- Small routing or normalisation fixtures for public, well-described text examples.
- Tests that expose dialect, code-switching, or annotation edge cases.
- Documentation improvements for responsible dataset release.
- Evaluation utilities that remain deterministic and dependency-light.
- Optional integrations with heavier NLP libraries, provided the core package still works without them.

## Before Opening a Pull Request

Run the local checks:

```bash
make check
```

If `make` is unavailable:

```bash
python3 scripts/quality_gate.py
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Data and Privacy

Do not commit private datasets, scraped personal data, credentials, API tokens, model weights, or files that cannot be redistributed. For data-related contributions, include the source, licence, collection context, intended use, and known limitations.

## Language Coverage

Language and dialect support should not be presented as identity detection. When adding examples, prefer clear, sourced, public examples and document uncertainty where the routing signal is ambiguous.

## Review Standard

Small pull requests with clear reasoning are easiest to review. The most useful explanation is usually why a design choice improves reliability, transparency, or responsible use.
