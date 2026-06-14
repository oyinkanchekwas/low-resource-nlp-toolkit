"""Small dataset readers for examples and experiments."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, Mapping, Optional


@dataclass(frozen=True)
class TextRecord:
    """A normalised representation of a text record."""

    text: str
    label: Optional[str] = None
    language: Optional[str] = None
    metadata: Mapping[str, str] = None


def iter_jsonl(path: str | Path) -> Iterator[Dict[str, object]]:
    """Yield JSON objects from a JSONL file."""

    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"JSONL line {line_number} must contain an object.")
            yield value


def iter_csv(path: str | Path) -> Iterator[Dict[str, str]]:
    """Yield rows from a CSV file as dictionaries."""

    with Path(path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield dict(row)


def iter_text_records(
    path: str | Path,
    *,
    text_field: str = "text",
    label_field: str = "label",
    language_field: str = "lang",
) -> Iterator[TextRecord]:
    """Yield `TextRecord` objects from CSV or JSONL files."""

    source = Path(path)
    rows = iter_jsonl(source) if source.suffix.lower() == ".jsonl" else iter_csv(source)
    for row in rows:
        text = str(row.get(text_field, ""))
        label = row.get(label_field)
        language = row.get(language_field)
        metadata = {str(key): str(value) for key, value in row.items() if key != text_field}
        yield TextRecord(
            text=text,
            label=str(label) if label is not None else None,
            language=str(language) if language is not None else None,
            metadata=metadata,
        )


def write_jsonl(path: str | Path, rows: Iterator[Mapping[str, object]]) -> int:
    """Write rows to JSONL and return the number written."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), ensure_ascii=False) + "\n")
            count += 1
    return count
