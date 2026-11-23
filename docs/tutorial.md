# Route a corpus

A profile file contains a source description and a list of routes. The demonstration below uses test vocabulary; its route identifiers do not denote languages.

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

Each profile requires `code` and `name`. Evidence fields are `keywords`, `stopwords`, and `unique_chars`, each a list of strings. At least one evidence field must be populated. Codes must be distinct; `und` and `ambiguous` are reserved for unassigned outcomes. A source description records the material used to construct the profiles; it does not establish permission to redistribute that material.

## CSV and JSONL input

This script reads a file with a `text` column or field and an optional `lang` field. It writes routing outcomes without copying the input text.

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

## Token audits

```python
from low_resource_nlp import LexicalLanguageRouter, audit_code_switching, load_profiles

router = LexicalLanguageRouter(load_profiles("examples/profiles.json"))
audit = audit_code_switching("alpha beta", router=router)
print(audit.to_aggregate_dict())
```

The full audit includes the original text and token evidence. Aggregate output contains counts and the code-switch ratio. It omits text, route names, and route codes. Offsets in the full output refer to the original input.

Evaluate profile changes and thresholds on development data. Keep evaluation records separate from profile construction, account for duplicate and document relationships, and state the annotation unit used as a reference.
