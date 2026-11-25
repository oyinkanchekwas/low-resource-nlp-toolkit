"""Command-line interface for the low-resource NLP toolkit."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import List

from ._version import __version__
from .audit import audit_code_switching
from .datasets import iter_csv, iter_jsonl
from .evaluation import classification_report
from .labels import RatingScale, label_to_valence_arousal
from .normalisation import normalise_text
from .routing import LexicalLanguageRouter, load_profiles


def _print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(
        description="Low-resource NLP pre-processing and routing tools."
    )
    parser.add_argument("--version", action="version", version=f"low-resource-nlp {__version__}")
    subcommands = parser.add_subparsers(dest="command", required=True)

    normalise = subcommands.add_parser("normalise", help="Normalise a text string.")
    normalise.add_argument("text")

    route = subcommands.add_parser("route", help="Route a text string to a language profile.")
    route.add_argument("text")
    route.add_argument("--profiles", required=True, type=Path)
    route.add_argument("--min-confidence", type=float, default=0.0)
    route.add_argument("--min-score-margin", type=float, default=0.0)

    audit = subcommands.add_parser("audit", help="Examine language changes within a text.")
    audit.add_argument("text")
    audit.add_argument("--profiles", required=True, type=Path)
    audit.add_argument("--min-confidence", type=float, default=0.55)
    audit.add_argument("--min-score-margin", type=float, default=0.75)

    label = subcommands.add_parser("label", help="Normalise an emotion label or read ratings.")
    label.add_argument("label")
    label.add_argument("--scale-min", type=float)
    label.add_argument("--scale-max", type=float)
    label.add_argument("--source")
    label.add_argument("--perspective")
    label.add_argument("--source-version")

    evaluate = subcommands.add_parser(
        "evaluate", help="Evaluate a CSV/JSONL file with truth and prediction fields."
    )
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

    if args.command in {"route", "audit"}:
        try:
            router = LexicalLanguageRouter(load_profiles(args.profiles))
            router.route_selectively(
                "",
                min_confidence=args.min_confidence,
                min_score_margin=args.min_score_margin,
            )
        except (OSError, TypeError, ValueError) as exc:
            parser.error(str(exc))

    if args.command == "route":
        result = router.route_selectively(
            args.text,
            min_confidence=args.min_confidence,
            min_score_margin=args.min_score_margin,
        )
        decision = result.decision
        _print_json(
            {
                "language_code": decision.language_code,
                "language_name": decision.language_name,
                "confidence": decision.confidence,
                "score_margin": result.score_margin,
                "accepted": result.accepted,
                "accepted_language_code": result.accepted_language_code,
                "accepted_language_name": result.accepted_language_name,
                "abstention_reason": result.abstention_reason,
                "scores": decision.scores,
                "signals": decision.signals,
            }
        )
        return 0

    if args.command == "audit":
        report = audit_code_switching(
            args.text,
            router=router,
            min_confidence=args.min_confidence,
            min_score_margin=args.min_score_margin,
        )
        _print_json(report.to_dict())
        return 0

    if args.command == "label":
        metadata = (args.scale_min, args.scale_max, args.source, args.perspective)
        try:
            if any(value is not None for value in metadata) or args.source_version is not None:
                scale = RatingScale(*metadata, version=args.source_version)
            else:
                scale = None
            mapping = label_to_valence_arousal(args.label, scale=scale)
        except (TypeError, ValueError) as exc:
            parser.error(str(exc))
        _print_json(
            {
                "original": mapping.original,
                "canonical": mapping.canonical,
                "valence": mapping.valence,
                "arousal": mapping.arousal,
                "scale": asdict(mapping.scale) if mapping.scale is not None else None,
            }
        )
        return 0

    if args.command == "evaluate":
        truth, predictions = [], []
        reader = iter_jsonl if args.path.suffix.lower() == ".jsonl" else iter_csv
        try:
            for number, row in enumerate(reader(args.path), start=1):
                for field, destination in (
                    (args.truth_field, truth),
                    (args.prediction_field, predictions),
                ):
                    value = row.get(field)
                    if (
                        value is None
                        or not isinstance(value, (str, int, float, bool))
                        or (isinstance(value, str) and not value.strip())
                        or (isinstance(value, float) and not math.isfinite(value))
                    ):
                        raise ValueError(
                            f"Record {number} requires a non-empty scalar in field {field!r}."
                        )
                    destination.append(str(value))
            if not truth:
                raise ValueError("Evaluation requires at least one labelled record.")
        except (OSError, UnicodeError, ValueError) as exc:
            parser.error(str(exc))
        _print_json(classification_report(truth, predictions))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
