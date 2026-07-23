"""Repository checks for release hygiene."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".cff",
    ".jsonl",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
}

BRITISH_ENGLISH = {
    r"\bbehavior\b": "behaviour",
    r"\bbehaviors\b": "behaviours",
    r"\bbehavioral\b": "behavioural",
    r"\bcolor\b": "colour",
    r"\bcolors\b": "colours",
    r"\banalyze\b": "analyse",
    r"\banalyzed\b": "analysed",
    r"\banalyzer\b": "analyser",
    r"\bartifact\b": "artefact",
    r"\bartifacts\b": "artefacts",
    r"\bmodeling\b": "modelling",
    r"\blabeled\b": "labelled",
    r"\blabeling\b": "labelling",
    r"\boptimize\b": "optimise",
    r"\boptimized\b": "optimised",
    r"\butilize\b": "use",
    r"\butilized\b": "used",
}

SECRET_PATTERNS = {
    r"\bsk-[A-Za-z0-9]{20,}\b": "OpenAI-style API key",
    r"\bAKIA[0-9A-Z]{16}\b": "AWS access key",
    r"\bAIza[0-9A-Za-z_-]{35}\b": "Google API key",
    r"\bghp_[0-9A-Za-z]{30,}\b": "GitHub personal access token",
}

ALLOWED_LINE_SNIPPETS = {
    "actions/upload-pages-artifact@",
    "unicodedata.normalize",
}


def is_scannable(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    if path.name == "LICENSE":
        return False
    return path.suffix in TEXT_SUFFIXES


def iter_scannable_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*") if path.is_file() and is_scannable(path))


def line_is_allowed(line: str) -> bool:
    return any(snippet in line for snippet in ALLOWED_LINE_SNIPPETS)


def check_language_and_secrets() -> list[str]:
    failures: list[str] = []
    for path in iter_scannable_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(ROOT)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line_is_allowed(line):
                continue
            for pattern, replacement in BRITISH_ENGLISH.items():
                if re.search(pattern, line, re.IGNORECASE):
                    failures.append(f"{rel}:{line_number}: prefer British English: {replacement}")
            for pattern, label in SECRET_PATTERNS.items():
                if re.search(pattern, line):
                    failures.append(f"{rel}:{line_number}: possible committed secret: {label}")
    return failures


def check_version_consistency() -> list[str]:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_file = (ROOT / "src" / "low_resource_nlp" / "_version.py").read_text(encoding="utf-8")
    pyproject_match = re.search(r'^version = "([^"]+)"', pyproject, flags=re.MULTILINE)
    source_match = re.search(r'^__version__ = "([^"]+)"', version_file, flags=re.MULTILINE)
    if not pyproject_match or not source_match:
        return ["Could not find package version in pyproject.toml or _version.py."]
    if pyproject_match.group(1) != source_match.group(1):
        return [
            "Version mismatch: "
            f"pyproject.toml={pyproject_match.group(1)} "
            f"_version.py={source_match.group(1)}"
        ]
    return []


def main() -> int:
    failures = check_language_and_secrets()
    failures.extend(check_version_consistency())
    if failures:
        print("Quality gate failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Quality gate passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
