# Triage a multilingual corpus

Short social and conversational texts are often ambiguous. A useful first pass should accept strong routes and send uncertain texts for review.

This example reads either CSV or JSONL, applies the default router and writes one JSON object per input record. The `accepted_language` field is empty when the score margin is below the threshold.

```python
import argparse
import json

from low_resource_nlp import LexicalLanguageRouter
from low_resource_nlp.datasets import iter_text_records


parser = argparse.ArgumentParser()
parser.add_argument("path")
parser.add_argument("--min-score-margin", type=float, default=0.75)
args = parser.parse_args()

router = LexicalLanguageRouter.default()

for record_number, record in enumerate(iter_text_records(args.path), start=1):
    route = router.route_selectively(
        record.text,
        min_score_margin=args.min_score_margin,
    )
    print(
        json.dumps(
            {
                "record": record_number,
                "expected_language": record.language,
                "proposed_language": route.decision.language_code,
                "accepted_language": route.accepted_language_code,
                "score_margin": route.score_margin,
                "abstention_reason": route.abstention_reason,
            },
            ensure_ascii=False,
        )
    )
```

Save the script as `route_corpus.py`, then run:

```bash
python route_corpus.py examples/sample_texts.jsonl > routes.jsonl
```

The original text is not written to the output in this example. That is useful when routing results need to be shared without reproducing the source material.

## Inspecting an uncertain record

The corpus pass identifies records for review. The audit API gives a closer look at one of them:

```python
from low_resource_nlp import audit_code_switching

audit = audit_code_switching("abeg make una check this model output")

for token in audit.tokens:
    print(token.text, token.accepted_language_code, token.score_margin, token.signals)
```

Token offsets in the audit refer to the original text, so a review interface can mark the exact evidence without re-tokenising the record.

## Measuring a policy

When corpus-level language labels are available, report coverage alongside accuracy. Accuracy among accepted records can rise simply because harder examples have been rejected.

```python
import json

from low_resource_nlp import LexicalLanguageRouter, selective_classification_report
from low_resource_nlp.datasets import iter_text_records

router = LexicalLanguageRouter.default()
truth = []
predictions = []
accepted = []

for record in iter_text_records("labelled_samples.jsonl"):
    route = router.route_selectively(record.text, min_score_margin=0.75)
    truth.append(record.language or "")
    predictions.append(route.decision.language_code)
    accepted.append(route.accepted)

report = selective_classification_report(truth, predictions, accepted)
print(json.dumps(report, indent=2))
```

Choose thresholds on development data, then keep them fixed for the test set. The [AfriSenti benchmark](benchmark.md) follows this split and records the selected policy, confidence intervals and per-language coverage.

## Before using the routes

- Check results separately for every language represented in the corpus.
- Keep diacritics unless the downstream method requires their removal.
- Review rejected and code-mixed records as a separate group; do not treat them as noise.
- Do not interpret a text route as a person's identity or language community.
