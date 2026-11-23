# Low-Resource NLP Toolkit

Python utilities for multilingual text preparation and evaluation. The package provides Unicode-aware normalisation, configurable lexical routing, token-level evidence audits, emotion-label mappings, and classification metrics.

Development version: `0.4.0.dev1`.

## Installation

From the source directory:

```bash
python -m pip install .
low-resource-nlp --version
```

## Routing

Routing requires language profiles supplied by the caller. Each profile specifies a code, a name, and lexical or character evidence. A JSON profile collection also records a source description. Use material you have permission to process.

The included profile file uses mechanical test vocabulary and example route identifiers:

```bash
low-resource-nlp route "alpha amber" --profiles examples/profiles.json
low-resource-nlp audit "alpha beta" --profiles examples/profiles.json
```

For your own data, supply your profile file through `--profiles`. The Python API accepts the same file:

```python
from low_resource_nlp import LexicalLanguageRouter, audit_code_switching, load_profiles

router = LexicalLanguageRouter(load_profiles("examples/profiles.json"))
route = router.route_selectively("alpha amber", min_score_margin=0.75)
audit = audit_code_switching("alpha beta", router=router)
print(route.accepted_language_code)
print(audit.to_aggregate_dict())
```

Routing scores describe relative evidence within the supplied profiles. Thresholds and language performance need evaluation on data appropriate to the intended task. Token audits expose evidence, offsets, and unassigned tokens; they do not provide independently annotated language labels.

## Text and emotion labels

```bash
low-resource-nlp normalise "ALPHA @user https://example.org"
low-resource-nlp label joy
low-resource-nlp label '0.5#0.7' --scale-min 0 --scale-max 1 --source 'my dataset' --perspective reader
```

Category names remain distinct unless a caller provides an explicit mapping. Dimensional ratings require a scale, source, and annotation perspective. See [Emotion labels and ratings](docs/labels.md).

## Evaluation

`classification_report` reports class-level metrics and a confusion matrix. `selective_classification_report` reports coverage and accuracy among accepted records, with undefined values represented explicitly. The [corpus tutorial](docs/tutorial.md) describes routing a CSV or JSONL file.

## Migration

The `route` and `audit` commands require `--profiles`. Construct a Python router with explicit profiles and pass it to `audit_code_switching`. Calling `LexicalLanguageRouter.default()` raises a configuration error. Emotion categories no longer receive automatic coordinates, and the previous category-list constant has been removed.

Earlier benchmark results concern version 0.3.0. See the [historical benchmark](docs/benchmark.md) for the original version and sources.

## Checks

```bash
make check
mkdocs build --strict
python -m build
```
