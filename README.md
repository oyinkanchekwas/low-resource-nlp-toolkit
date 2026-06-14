# Low-Resource NLP Toolkit

A public, research-facing Python toolkit for African language pre-processing, emotion-label mapping, evaluation, and language/dialect routing.

The project is designed as a safe open-source wrapper around the kinds of NLP engineering problems that appear in low-resource and multilingual AI research: noisy text, code-switching, uneven label taxonomies, small datasets, and evaluation that must be transparent.

## Why This Exists

Low-resource NLP projects often spend too much time rebuilding the same foundations before modelling begins. This toolkit provides a dependable base layer:

- Text normalisation for noisy social, conversational, and cultural text.
- Lightweight African language routing for Yoruba, Igbo, Hausa, Nigerian Pidgin, Swahili, and English.
- Emotion label harmonisation across categorical and valence-arousal formats.
- Evaluation utilities for classification and routing experiments.
- A CLI and examples that run without downloading model weights.
- Extension points for transformer or embedding backends when a project needs heavier models.

## Architecture

```mermaid
flowchart LR
    A["Raw multilingual text"] --> B["Normaliser"]
    B --> C["Tokeniser"]
    C --> D["Language router"]
    C --> E["Emotion label mapper"]
    D --> F["Route decision + confidence"]
    E --> G["Canonical emotion / valence-arousal"]
    F --> H["Evaluation reports"]
    G --> H
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Route a text sample:

```bash
low-resource-nlp route "abeg make una help me check this model output"
```

Normalise text:

```bash
low-resource-nlp normalise "Ẹ káàrọ̀!!! Visit https://example.com @user"
```

Map an emotion label:

```bash
low-resource-nlp label joy
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

## Python Usage

```python
from low_resource_nlp import LexicalLanguageRouter, normalise_text, label_to_valence_arousal

text = normalise_text("Ẹ káàrọ̀, báwo ni?")
decision = LexicalLanguageRouter.default().route(text)
emotion = label_to_valence_arousal("joy")

print(decision.language_code, decision.confidence)
print(emotion)
```

## Current Scope

The first public release deliberately avoids bundling private datasets or model weights. The core is deterministic, inspectable, and dependency-light. Later releases can add optional embedding and transformer backends while keeping the same interfaces.

Supported core modules:

- `normalisation`: Unicode-aware text cleaning, URL/user normalisation, tokenisation, repeated-character handling.
- `routing`: script-aware and lexicon-assisted language routing.
- `labels`: canonical emotion labels and valence-arousal mapping.
- `evaluation`: precision, recall, F1, macro/micro summaries, and confusion matrices.
- `datasets`: simple CSV/JSONL readers for experiment scaffolding.

## Roadmap

- Add benchmark fixtures using public African language datasets.
- Add optional sentence-transformer routing backends.
- Add dialect-sensitive Yoruba and Nigerian Pidgin examples.
- Add model cards and data statements for responsible release practices.
- Add Hugging Face dataset/model integration examples without committing large artefacts.

## Responsible AI Notes

This toolkit is for research and prototyping. Language, dialect, and emotion labels are socially and culturally sensitive. Do not treat routing or emotion predictions as identity labels, clinical assessments, or ground truth. Always evaluate with speakers, domain experts, and context-specific data.
