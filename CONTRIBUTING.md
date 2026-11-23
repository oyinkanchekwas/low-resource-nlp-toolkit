# Contributing

Include tests for changed behaviour and enough detail to reproduce the result.

## Checks

Run `make check`, `ruff check .`, and `ruff format --check .` before submitting a change. Documentation changes should also pass `mkdocs build --strict`.

## Profiles and data

Routing profiles must identify their source and use material that can be shared under the applicable terms. Software examples should use mechanical fixtures or source-qualified text.

Keep private datasets, credentials, model weights, and restricted records out of contributions. Describe dataset permissions and attribution where they apply.

## Research results

State the reference labels, evaluation unit, and split used for reported results. Account for code-mixing and repeated records. Changes to profiles or thresholds need their own evaluation; historical results remain associated with their original configuration.
