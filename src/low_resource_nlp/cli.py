"""Command-line interface for the low-resource NLP toolkit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from .datasets import iter_text_records
from .evaluation import classification_report
from .labels import label_to_valence_arousal
from .normalisation import normalise_text
from .routing import LexicalLanguageRouter


def _print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(description="Low-resource NLP pre-processing and routing tools.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    normalise = subcommands.add_parser("normalise", help="Normalise a text string.")
    normalise.add_argument("text")

    route = subcommands.add_parser("route", help="Route a text string to a language profile.")
    route.add_argument("text")

    label = subcommands.add_parser("label", help="Map an emotion label to the canonical taxonomy.")
    label.add_argument("label")

    evaluate = subcommands.add_parser("evaluate", help="Evaluate a CSV/JSONL file with truth and prediction fields.")
    evaluate.add_argument("path", type=Path)
    evaluate.add_argument("--truth-field", default="label")
    evaluate.add_argument("--prediction-field", default="prediction")

    return parser


def main(argv: List[str] | None = None) -> int:
    """Run the CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "normalise":
        print(normalise_text(args.text))
        return 0

    if args.command == "route":
        decision = LexicalLanguageRouter.default().route(args.text)
        _print_json(
            {
                "language_code": decision.language_code,
                "language_name": decision.language_name,
                "confidence": decision.confidence,
                "scores": decision.scores,
                "signals": decision.signals,
            }
        )
        return 0

    if args.command == "label":
        mapping = label_to_valence_arousal(args.label)
        _print_json(
            {
                "original": mapping.original,
                "canonical": mapping.canonical,
                "valence": mapping.valence,
                "arousal": mapping.arousal,
            }
        )
        return 0

    if args.command == "evaluate":
        records = list(
            iter_text_records(
                args.path,
                label_field=args.truth_field,
            )
        )
        truth = [record.label or "" for record in records]
        predictions = [str(record.metadata.get(args.prediction_field, "")) for record in records]
        _print_json(classification_report(truth, predictions))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
