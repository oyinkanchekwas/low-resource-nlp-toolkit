# Technical scope

## Package modules

- Deterministic normalisation and tokenisation.
- Canonical emotion-label and valence-arousal mapping.
- Lexical and script-aware language routing.
- Selective routing with explicit abstention reasons.
- Token-level code-switch audits.
- Classification, confusion-matrix and coverage-aware evaluation.
- CSV and JSONL readers for small experiments.

The core package has no third-party runtime dependencies. This keeps its decisions inspectable and makes it practical in teaching environments or as a baseline before heavier models are introduced.

## Evaluation

The AfriSenti benchmark measures corpus-language routing for Hausa, Igbo, Nigerian Pidgin, Swahili and Yoruba. Thresholds are selected on development data and applied unchanged to the test split. The benchmark also repeats each test prediction after diacritic removal, allowing the effect of that normalisation choice to be measured on paired examples.

AfriSenti labels identify the source corpus rather than every token in a tweet. Because the data includes code-mixing, the report does not claim word-level language-identification accuracy.

## Data and privacy

- No private datasets are bundled.
- No model weights are committed.
- No credentials are required.
- Benchmark source files are downloaded from a pinned public revision and checked against recorded hashes.
- Reports contain aggregate measurements rather than source tweets.

## Adding a language or benchmark

Language profiles should include tests that show both strong evidence and ambiguous cases. Benchmark additions need a public source, a redistribution-compatible licence, fixed input hashes, a documented split policy and a clear account of limitations.
