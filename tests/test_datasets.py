from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from low_resource_nlp.datasets import TextRecord, iter_text_records, write_jsonl


class DatasetTests(unittest.TestCase):
    def test_iter_text_records_from_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.jsonl"
            path.write_text('{"text":"hello","label":"joy","lang":"eng"}\n', encoding="utf-8")
            records = list(iter_text_records(path))

        self.assertEqual(records[0].text, "hello")
        self.assertEqual(records[0].label, "joy")
        self.assertEqual(records[0].language, "eng")
        self.assertEqual(records[0].metadata["label"], "joy")

    def test_text_record_metadata_defaults_to_empty_mapping(self) -> None:
        record = TextRecord(text="hello")
        self.assertEqual(record.metadata, {})

    def test_write_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.jsonl"
            count = write_jsonl(path, iter([{"text": "hello"}]))
            text = path.read_text(encoding="utf-8")

        self.assertEqual(count, 1)
        self.assertIn("hello", text)


if __name__ == "__main__":
    unittest.main()
