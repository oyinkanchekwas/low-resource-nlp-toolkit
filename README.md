# Low-Resource NLP Toolkit

Python tools for multilingual text preparation, code-switching analysis, emotion labels, and classification evaluation.

Version: `0.4.0`.

## Installation

From the source directory:

```bash
python -m pip install .
low-resource-nlp --version
```

## Routing

Define the languages you want to recognise in a JSON profile. Give each language a code and a name, then add words or distinctive characters to match. Describe the material used to build the profiles and check its reuse conditions.

The example at `examples/profiles.json` defines two routes, `a` and `b`, using a small test vocabulary:

```bash
low-resource-nlp route "alpha amber" --profiles examples/profiles.json
low-resource-nlp audit "alpha beta" --profiles examples/profiles.json
```

Replace the example path with the path to your language profiles when processing your text. The Python API reads the same JSON format:

```python
from low_resource_nlp import LexicalLanguageRouter, audit_code_switching, load_profiles

router = LexicalLanguageRouter(load_profiles("examples/profiles.json"))
route = router.route_selectively("alpha amber", min_score_margin=0.75)
result = audit_code_switching("alpha beta", router=router)
print(route.accepted_language_code)
print(result.to_aggregate_dict())
```

With mixed-language text, you can see which words match each language profile and where the suggested language changes within a sentence. Test your profiles and thresholds against labelled examples from the setting where you plan to use the toolkit.

## Text and emotion labels

```bash
low-resource-nlp normalise "ALPHA @user https://example.org"
low-resource-nlp label joy
low-resource-nlp label '0.5#0.7' --scale-min 0 --scale-max 1 --source 'my dataset' --perspective reader
```

Category names remain distinct unless a caller supplies a mapping. Dimensional ratings require a scale, source, and annotation perspective. See [Emotion labels and ratings](https://oyinkanchekwas.github.io/low-resource-nlp-toolkit/labels/).

## Evaluation

`classification_report` reports class-level metrics and a confusion matrix. `selective_classification_report` reports coverage and accuracy among accepted records. Undefined metrics use `None` in Python and `null` in JSON. The [corpus tutorial](https://oyinkanchekwas.github.io/low-resource-nlp-toolkit/tutorial/) describes routing a CSV or JSONL file.

The `evaluate` command requires a non-empty CSV or JSONL file with `label` and `prediction` fields. Use `--truth-field` and `--prediction-field` for other column names. Missing, null, blank, structured, or non-finite labels are rejected before scoring; numeric zero is a valid label.

## Migration

The `route` and `audit` commands take a `--profiles` path. In Python, construct `LexicalLanguageRouter(load_profiles(path))` and pass the router to `audit_code_switching`. Replace calls to `LexicalLanguageRouter.default()` with this pattern. Use `aliases` for category mappings and `coordinates` with a `RatingScale` for dimensional values. Remove imports of the old category-list constant.

Earlier benchmark results concern version 0.3.0. See the [historical benchmark](https://oyinkanchekwas.github.io/low-resource-nlp-toolkit/benchmark/) for the original version and sources.

## Feedback

[Share your experience](https://github.com/oyinkanchekwas/low-resource-nlp-toolkit/issues/new?template=usage_feedback.yml). Tell me how you are using the toolkit and what would make it more useful.

## Checks

```bash
make check
mkdocs build --strict
python -m build
```
