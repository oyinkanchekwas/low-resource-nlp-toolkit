"""Run the held-out AfriSenti routing and orthography benchmark."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from low_resource_nlp import __version__
from low_resource_nlp.evaluation import (
    classification_report,
    selective_classification_report,
)
from low_resource_nlp.normalisation import strip_diacritics
from low_resource_nlp.routing import LexicalLanguageRouter, load_profiles, score_margin

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path(__file__).with_name("manifest.json")
LANGUAGES = ("hau", "ibo", "pcm", "swa", "yor")
RAW_ROOT = "https://raw.githubusercontent.com"


@dataclass(frozen=True)
class RoutingPrediction:
    """One gold corpus label and two paired routing decisions."""

    truth: str
    prediction: str
    confidence: float
    score_margin: float
    stripped_prediction: str
    stripped_confidence: float
    stripped_score_margin: float


def read_manifest(path: Path = MANIFEST_PATH) -> Mapping[str, object]:
    """Read the pinned dataset manifest."""

    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    """Hash a file incrementally in fixed-size chunks."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, expected_sha256: str) -> None:
    """Raise when a benchmark input is absent or differs from the manifest."""

    if not path.exists():
        raise FileNotFoundError(f"Benchmark input not found: {path}")
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise ValueError(
            f"SHA-256 mismatch for {path.name}: expected {expected_sha256}, found {actual}"
        )


def _raw_url(repository: str, revision: str, source_path: str) -> str:
    owner_repo = repository.removeprefix("https://github.com/").strip("/")
    return f"{RAW_ROOT}/{owner_repo}/{revision}/{source_path}"


def prepare_data(manifest: Mapping[str, object], data_dir: Path, download: bool) -> None:
    """Download missing files when requested, then verify every input hash."""

    dataset = manifest["dataset"]
    files = manifest["files"]
    if not isinstance(dataset, dict) or not isinstance(files, list):
        raise ValueError("The benchmark manifest has an invalid structure.")

    repository = str(dataset["repository"])
    revision = str(dataset["revision"])
    data_dir.mkdir(parents=True, exist_ok=True)

    for entry in files:
        if not isinstance(entry, dict):
            raise ValueError("Each manifest file entry must be an object.")
        target = data_dir / str(entry["local_name"])
        expected_hash = str(entry["sha256"])
        try:
            verify_file(target, expected_hash)
            continue
        except (FileNotFoundError, ValueError):
            if not download:
                raise

        url = _raw_url(repository, revision, str(entry["path"]))
        request = urllib.request.Request(url, headers={"User-Agent": "low-resource-nlp-benchmark"})
        partial = target.with_suffix(target.suffix + ".part")
        with urllib.request.urlopen(request) as response, partial.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        verify_file(partial, expected_hash)
        partial.replace(target)


def load_predictions(
    manifest: Mapping[str, object],
    data_dir: Path,
    split: str,
    router: LexicalLanguageRouter,
) -> list[RoutingPrediction]:
    """Route one split while retaining paired diacritic-stripped decisions."""

    predictions: list[RoutingPrediction] = []
    files = manifest["files"]
    if not isinstance(files, list):
        raise ValueError("The benchmark manifest has an invalid file list.")

    for entry in files:
        if not isinstance(entry, dict) or entry.get("split") != split:
            continue
        truth = str(entry["language"])
        source = data_dir / str(entry["local_name"])
        with source.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if not reader.fieldnames or "tweet" not in reader.fieldnames:
                raise ValueError(f"Expected a tweet column in {source}")
            for row in reader:
                text = row.get("tweet", "")
                original = router.route(text)
                stripped = router.route(strip_diacritics(text))
                predictions.append(
                    RoutingPrediction(
                        truth=truth,
                        prediction=original.language_code,
                        confidence=original.confidence,
                        score_margin=score_margin(original.scores),
                        stripped_prediction=stripped.language_code,
                        stripped_confidence=stripped.confidence,
                        stripped_score_margin=score_margin(stripped.scores),
                    )
                )
    return predictions


def is_accepted(
    prediction: RoutingPrediction,
    min_confidence: float,
    min_score_margin: float,
    *,
    stripped: bool = False,
) -> bool:
    """Apply a selective routing policy to an original or stressed decision."""

    if stripped:
        route = prediction.stripped_prediction
        confidence = prediction.stripped_confidence
        margin = prediction.stripped_score_margin
    else:
        route = prediction.prediction
        confidence = prediction.confidence
        margin = prediction.score_margin
    return route != "und" and confidence >= min_confidence and margin >= min_score_margin


def policy_report(
    predictions: Sequence[RoutingPrediction],
    min_confidence: float,
    min_score_margin: float,
    *,
    stripped: bool = False,
) -> Mapping[str, object]:
    """Evaluate one routing policy with binomial confidence intervals."""

    truth = [item.truth for item in predictions]
    routes = [item.stripped_prediction if stripped else item.prediction for item in predictions]
    accepted = [
        is_accepted(
            item,
            min_confidence,
            min_score_margin,
            stripped=stripped,
        )
        for item in predictions
    ]
    report = dict(selective_classification_report(truth, routes, accepted, labels=LANGUAGES))
    correct = sum(
        keep and expected == predicted for expected, predicted, keep in zip(truth, routes, accepted)
    )
    report.update(
        {
            "min_confidence": round(min_confidence, 4),
            "min_score_margin": round(min_score_margin, 4),
            "coverage_ci95": wilson_interval(sum(accepted), len(accepted)),
            "selective_accuracy_ci95": wilson_interval(correct, sum(accepted)),
        }
    )
    return report


def choose_policy(
    predictions: Sequence[RoutingPrediction],
    target_accuracy: float,
    confidence_grid: Iterable[float] | None = None,
    margin_grid: Iterable[float] | None = None,
) -> Mapping[str, object]:
    """Choose the highest-coverage policy meeting a development accuracy target."""

    confidences = tuple(confidence_grid or (step / 20 for step in range(20)))
    margins = tuple(margin_grid or (step / 4 for step in range(17)))
    candidates: list[Mapping[str, object]] = []
    for confidence in confidences:
        for margin in margins:
            report = policy_report(predictions, confidence, margin)
            if (
                report["selective_accuracy"] is not None
                and float(report["selective_accuracy"]) >= target_accuracy
            ):
                candidates.append(report)
    if not candidates:
        raise ValueError(f"No policy reached development accuracy {target_accuracy:.3f}.")
    return max(
        candidates,
        key=lambda item: (
            float(item["coverage"]),
            float(item["selective_accuracy"]),
            -float(item["min_confidence"]),
            -float(item["min_score_margin"]),
        ),
    )


def wilson_interval(successes: int, total: int, z: float = 1.96) -> list[float] | None:
    """Return a two-sided Wilson interval for a binomial proportion."""

    if total == 0 and successes == 0:
        return None
    if total <= 0 or successes < 0 or successes > total:
        raise ValueError("Successes must be between zero and the total.")
    proportion = successes / total
    denominator = 1.0 + (z * z / total)
    centre = (proportion + z * z / (2 * total)) / denominator
    spread = (
        z * math.sqrt((proportion * (1 - proportion) + z * z / (4 * total)) / total) / denominator
    )
    return [round(max(0.0, centre - spread), 4), round(min(1.0, centre + spread), 4)]


def baseline_report(predictions: Sequence[RoutingPrediction]) -> Mapping[str, object]:
    """Report ordinary routing accuracy with no abstention."""

    truth = [item.truth for item in predictions]
    routes = [item.prediction for item in predictions]
    report = dict(classification_report(truth, routes, labels=LANGUAGES))
    correct = sum(expected == predicted for expected, predicted in zip(truth, routes))
    report["total"] = len(predictions)
    report["accuracy_ci95"] = wilson_interval(correct, len(predictions))
    return report


def _paired_difference_interval(differences: Sequence[int]) -> list[float]:
    if not differences:
        return [0.0, 0.0]
    mean = sum(differences) / len(differences)
    if len(differences) == 1:
        return [round(mean, 4), round(mean, 4)]
    variance = sum((value - mean) ** 2 for value in differences) / (len(differences) - 1)
    spread = 1.96 * math.sqrt(variance / len(differences))
    return [round(mean - spread, 4), round(mean + spread, 4)]


def orthography_report(
    predictions: Sequence[RoutingPrediction],
    min_confidence: float,
    min_score_margin: float,
) -> Mapping[str, object]:
    """Measure paired route changes after removing diacritics."""

    original_correct = [item.prediction == item.truth for item in predictions]
    stripped_correct = [item.stripped_prediction == item.truth for item in predictions]
    differences = [
        int(stripped) - int(original)
        for original, stripped in zip(original_correct, stripped_correct)
    ]

    per_language: dict[str, Mapping[str, object]] = {}
    for language in LANGUAGES:
        rows = [item for item in predictions if item.truth == language]
        original = sum(item.prediction == language for item in rows)
        stripped = sum(item.stripped_prediction == language for item in rows)
        flips = sum(item.prediction != item.stripped_prediction for item in rows)
        per_language[language] = {
            "support": len(rows),
            "original_accuracy": round(original / len(rows), 4),
            "stripped_accuracy": round(stripped / len(rows), 4),
            "accuracy_difference": round((stripped - original) / len(rows), 4),
            "route_flip_rate": round(flips / len(rows), 4),
        }

    return {
        "original_accuracy": round(sum(original_correct) / len(predictions), 4),
        "stripped_accuracy": round(sum(stripped_correct) / len(predictions), 4),
        "accuracy_difference": round(sum(differences) / len(differences), 4),
        "accuracy_difference_ci95": _paired_difference_interval(differences),
        "route_flip_rate": round(
            sum(item.prediction != item.stripped_prediction for item in predictions)
            / len(predictions),
            4,
        ),
        "original_policy": policy_report(
            predictions,
            min_confidence,
            min_score_margin,
        ),
        "stripped_policy": policy_report(
            predictions,
            min_confidence,
            min_score_margin,
            stripped=True,
        ),
        "languages": per_language,
    }


def build_report(
    manifest: Mapping[str, object],
    development: Sequence[RoutingPrediction],
    test: Sequence[RoutingPrediction],
    target_accuracy: float,
    *,
    profile_sha256: str,
) -> Mapping[str, object]:
    """Build the complete aggregate benchmark report."""

    if not re.fullmatch(r"[0-9a-f]{64}", profile_sha256):
        raise ValueError("A SHA-256 digest of the profile file is required.")
    selected = choose_policy(development, target_accuracy)
    confidence = float(selected["min_confidence"])
    margin = float(selected["min_score_margin"])
    return {
        "schema_version": 2,
        "toolkit_version": __version__,
        "profiles": {"sha256": profile_sha256},
        "dataset": manifest["dataset"],
        "task": "corpus-language routing",
        "languages": list(LANGUAGES),
        "development": {
            "baseline": baseline_report(development),
            "selection_target_accuracy": target_accuracy,
            "selected_policy": selected,
        },
        "test": {
            "baseline": baseline_report(test),
            "selected_policy": policy_report(test, confidence, margin),
            "orthography_stress": orthography_report(test, confidence, margin),
        },
    }


def _percentage(value: object) -> str:
    if value is None:
        return "N/A"
    return f"{100 * float(value):.2f}%"


def render_markdown(report: Mapping[str, object]) -> str:
    """Render the aggregate report as a concise research note."""

    dataset = report["dataset"]
    development = report["development"]
    test = report["test"]
    if (
        not isinstance(dataset, dict)
        or not isinstance(development, dict)
        or not isinstance(test, dict)
    ):
        raise ValueError("Report sections have an invalid structure.")
    dev_baseline = development["baseline"]
    dev_policy = development["selected_policy"]
    test_baseline = test["baseline"]
    test_policy = test["selected_policy"]
    stress = test["orthography_stress"]
    if not all(
        isinstance(section, dict)
        for section in (dev_baseline, dev_policy, test_baseline, test_policy, stress)
    ):
        raise ValueError("Report metrics have an invalid structure.")

    lines = [
        "# AfriSenti Routing Benchmark",
        "",
        (
            "This benchmark measures corpus-language routing on the AfriSenti development and "
            "test sets for Hausa, Igbo, Nigerian Pidgin, Swahili, and Yoruba. The router is "
            "dependency-light and uses inspectable lexical, character, and script evidence."
        ),
        "",
        "## Data",
        "",
        f"- Dataset: [{dataset['name']}]({dataset['repository']})",
        f"- Source revision: `{str(dataset['revision'])[:12]}`",
        f"- Toolkit version: `{report['toolkit_version']}`",
        f"- Profile file SHA-256: `{report['profiles']['sha256']}`",
        f"- Licence: {dataset['licence']}",
        f"- Task paper: [SemEval-2023 Task 12]({dataset['paper']})",
        "- Dataset paper: [AfriSenti](https://aclanthology.org/2023.emnlp-main.862/)",
        "- Related datasets: [NaijaSenti](https://aclanthology.org/2022.lrec-1.63/) and [ASAB](https://aclanthology.org/2020.coling-main.91/)",
        "- Source tweets reside in local, hash-checked data files.",
        "",
        "## Policy selection",
        "",
        (
            "The confidence and score-margin thresholds were selected on development data. "
            f"The search maximised coverage among policies reaching "
            f"{_percentage(development['selection_target_accuracy'])} selective accuracy."
        ),
        "",
        "| Split | Examples | Baseline accuracy | Coverage | Selective accuracy |",
        "| --- | ---: | ---: | ---: | ---: |",
        (
            f"| Development | {dev_baseline['total']:,} | {_percentage(dev_baseline['accuracy'])} "
            f"| {_percentage(dev_policy['coverage'])} | {_percentage(dev_policy['selective_accuracy'])} |"
        ),
        (
            f"| Test | {test_baseline['total']:,} | {_percentage(test_baseline['accuracy'])} "
            f"| {_percentage(test_policy['coverage'])} | {_percentage(test_policy['selective_accuracy'])} |"
        ),
        "",
        (
            f"Selected thresholds: confidence >= {float(dev_policy['min_confidence']):.2f}; "
            f"score margin >= {float(dev_policy['min_score_margin']):.2f}."
        ),
        "",
        "## Orthography stress test",
        "",
        (
            "Each test tweet was routed again after removing diacritics. This paired test "
            "isolates the effect of a common normalisation choice while keeping the text and "
            "corpus label fixed."
        ),
        "",
        "| Language | Examples | Original accuracy | Diacritics removed | Difference | Route flips |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    language_metrics = stress["languages"]
    if not isinstance(language_metrics, dict):
        raise ValueError("Orthography language metrics have an invalid structure.")
    for language in LANGUAGES:
        metrics = language_metrics[language]
        lines.append(
            f"| {language} | {metrics['support']:,} | {_percentage(metrics['original_accuracy'])} "
            f"| {_percentage(metrics['stripped_accuracy'])} "
            f"| {_percentage(metrics['accuracy_difference'])} "
            f"| {_percentage(metrics['route_flip_rate'])} |"
        )
    lines.extend(
        [
            "",
            (
                f"Across all test examples, accuracy changed from "
                f"{_percentage(stress['original_accuracy'])} to "
                f"{_percentage(stress['stripped_accuracy'])}. The paired difference was "
                f"{_percentage(stress['accuracy_difference'])}, with a 95% interval of "
                f"{_percentage(stress['accuracy_difference_ci95'][0])} to "
                f"{_percentage(stress['accuracy_difference_ci95'][1])}."
            ),
            "",
            "## Interpreting the results",
            "",
            (
                "The selected policy trades coverage for fewer accepted errors. Its score margin "
                "is a ranking gap. Probability estimates require calibration against annotated "
                "outcomes. The held-out result "
                "measures this fixed router on this corpus."
            ),
            "",
            (
                "This evaluation scores the route of each whole tweet against its source-corpus "
                "label. Token-level assessment requires language annotations for each token. "
                "Code-mixed tweets can contain English tokens within a Hausa or Nigerian Pidgin "
                "corpus."
            ),
            "",
            "## Reproduce",
            "",
            "Use a profile file matching the recorded SHA-256 digest and the pinned dataset files.",
            "",
            "```bash",
            (
                "PYTHONPATH=src python3 benchmarks/afrisenti/run_benchmark.py "
                "--profiles profiles.json --data-dir .benchmark-data/afrisenti-5aec3cf "
                f"--target-accuracy {float(development['selection_target_accuracy'])} "
                "--json-output benchmark-output/report.json "
                "--markdown-output benchmark-output/report.md"
            ),
            "```",
            "",
            "The JSON report contains confidence intervals, per-language coverage and confusion matrices.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the pinned AfriSenti routing benchmark.")
    parser.add_argument("--profiles", required=True, type=Path)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / ".benchmark-data" / "afrisenti-5aec3cf",
    )
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--target-accuracy", type=float, default=0.90)
    parser.add_argument(
        "--json-output",
        type=Path,
        help="New JSON output file; defaults to a separate benchmark-run directory.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        help="New Markdown output file; defaults to a separate benchmark-run directory.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not 0.0 < args.target_accuracy <= 1.0:
        raise ValueError("target-accuracy must be greater than 0 and no more than 1.")

    for output in (args.json_output, args.markdown_output):
        if output is not None and output.exists():
            parser.error("Output files must be new files.")
    if (
        args.json_output is not None
        and args.markdown_output is not None
        and args.json_output.resolve() == args.markdown_output.resolve()
    ):
        parser.error("JSON and Markdown outputs must use distinct files.")
    profile_sha256 = sha256_file(args.profiles)
    router = LexicalLanguageRouter(load_profiles(args.profiles))
    if profile_sha256 != sha256_file(args.profiles):
        raise ValueError("The profile file changed while it was being loaded.")
    manifest = read_manifest()
    prepare_data(manifest, args.data_dir, args.download)
    development = load_predictions(manifest, args.data_dir, "development", router)
    test = load_predictions(manifest, args.data_dir, "test", router)
    report = build_report(
        manifest, development, test, args.target_accuracy, profile_sha256=profile_sha256
    )

    if args.json_output is None or args.markdown_output is None:
        output_root = ROOT / ".benchmark-data" / "afrisenti-runs"
        output_root.mkdir(parents=True, exist_ok=True)
        output_directory = Path(tempfile.mkdtemp(prefix="run-", dir=output_root))
        if args.json_output is None:
            args.json_output = output_directory / "report.json"
        if args.markdown_output is None:
            args.markdown_output = output_directory / "report.md"
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_markdown(report)
    with args.json_output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    with args.markdown_output.open("x", encoding="utf-8") as stream:
        stream.write(rendered)

    selected = report["test"]["selected_policy"]
    print(
        f"test coverage={_percentage(selected['coverage'])} "
        f"selective_accuracy={_percentage(selected['selective_accuracy'])}"
    )
    print(f"JSON report: {args.json_output}")
    print(f"Markdown report: {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
