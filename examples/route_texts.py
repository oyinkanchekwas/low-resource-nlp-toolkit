"""Route supplied text with a caller-supplied profile collection."""

import argparse
import json

from low_resource_nlp import LexicalLanguageRouter, load_profiles


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    parser.add_argument("--profiles", required=True)
    parser.add_argument("--min-score-margin", type=float, default=0.75)
    args = parser.parse_args()
    router = LexicalLanguageRouter(load_profiles(args.profiles))
    result = router.route_selectively(args.text, min_score_margin=args.min_score_margin)
    print(
        json.dumps(
            {
                "accepted_language": result.accepted_language_code,
                "score_margin": result.score_margin,
                "abstention_reason": result.abstention_reason,
            }
        )
    )


if __name__ == "__main__":
    main()
