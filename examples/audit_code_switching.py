"""Report aggregate token evidence using supplied profiles."""

import argparse
import json

from low_resource_nlp import LexicalLanguageRouter, audit_code_switching, load_profiles


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    parser.add_argument("--profiles", required=True)
    args = parser.parse_args()
    router = LexicalLanguageRouter(load_profiles(args.profiles))
    report = audit_code_switching(args.text, router=router)
    print(json.dumps(report.to_aggregate_dict()))


if __name__ == "__main__":
    main()
