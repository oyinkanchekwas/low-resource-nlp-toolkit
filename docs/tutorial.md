# Route a corpus

A profile file contains a source description and a list of routes. The demonstration below uses test vocabulary with route identifiers `a` and `b`.

```json
{
  "source": "Mechanical demonstration vocabulary",
  "profiles": [
    {"code": "a", "name": "Example A", "keywords": ["alpha", "amber"]},
    {"code": "b", "name": "Example B", "keywords": ["beta", "bravo"]}
  ]
}
```

The source distribution includes this configuration at `examples/profiles.json`. With a wheel installation, create a JSON file using the configuration above or supply your own authorised profile collection.

Each profile requires `code` and `name`. Evidence fields are `keywords`, `stopwords`, and `unique_chars`, each a list of strings. At least one evidence field must be populated. Codes must be distinct; `und` and `ambiguous` are reserved for unassigned outcomes. A source description identifies the material used to construct the profiles. Reuse and redistribution follow that material's licence and access conditions.

The Python API accepts list or tuple evidence fields and stores an immutable snapshot. Character evidence uses the same NFC and lowercase normalisation as the input, with diacritics preserved. Equivalent character entries contribute one signal.

## CSV and JSONL input

This script reads a file with a `text` column or field and an optional `lang` field. Output records contain the input row number, reference language, accepted route, score margin, and abstention reason.

```python
import argparse
import json

from low_resource_nlp import LexicalLanguageRouter, load_profiles
from low_resource_nlp.datasets import iter_text_records

parser = argparse.ArgumentParser()
parser.add_argument("path")
parser.add_argument("--profiles", required=True)
parser.add_argument("--min-score-margin", type=float, default=0.75)
args = parser.parse_args()

router = LexicalLanguageRouter(load_profiles(args.profiles))
for number, record in enumerate(iter_text_records(args.path), start=1):
    result = router.route_selectively(record.text, min_score_margin=args.min_score_margin)
    print(
        json.dumps(
            {
                "record": number,
                "reference_language": record.language,
                "accepted_language": result.accepted_language_code,
                "score_margin": result.score_margin,
                "abstention_reason": result.abstention_reason,
            },
            ensure_ascii=False,
        )
    )
```

With this script in `route_corpus.py`, run:

```bash
python route_corpus.py my_texts.jsonl --profiles examples/profiles.json
```

For a mechanical smoke test, a JSONL file can contain:

```json
{"text": "alpha amber", "lang": "a"}
{"text": "beta bravo", "lang": "b"}
```

## Examining code-switching

```python
from low_resource_nlp import LexicalLanguageRouter, audit_code_switching, load_profiles

router = LexicalLanguageRouter(load_profiles("examples/profiles.json"))
result = audit_code_switching("alpha beta", router=router)
print(result.to_aggregate_dict())
```

Use the word-level results to examine where a sentence changes language. Each word is linked to its position in the input, so you can compare the suggested language with a reference annotation. The `to_dict()` method returns the input text alongside these results. Call `to_aggregate_dict()` for counts and the code-switch ratio.

Evaluate profile changes and thresholds on development data. Keep evaluation records separate from profile construction, account for duplicate and document relationships, and state the annotation unit used as a reference.
