import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from low_resource_nlp.cli import main


class EvaluationInputTests(unittest.TestCase):
    def invoke(self, content, suffix=".jsonl", options=()):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ("input" + suffix)
            path.write_text(content, encoding="utf-8")
            output, error = io.StringIO(), io.StringIO()
            with redirect_stdout(output), redirect_stderr(error):
                try:
                    status = main(["evaluate", str(path), *options])
                except SystemExit as exc:
                    status = exc.code
            return status, output.getvalue(), error.getvalue()

    def test_missing_or_empty_fields_fail_without_metrics(self):
        records = [
            {"text": "PRIVATE_TEXT"},
            {"label": "a"},
            {"prediction": "a"},
            {"label": None, "prediction": "a"},
            {"label": "a", "prediction": None},
            {"label": "", "prediction": ""},
            {"label": " ", "prediction": "a"},
            {"label": "a", "prediction": "\t"},
            {"label": ["a"], "prediction": "a"},
            {"label": "a", "prediction": {"value": "a"}},
            {"label": float("nan"), "prediction": "a"},
        ]
        for row in records:
            with self.subTest(row=row):
                status, output, error = self.invoke(json.dumps(row) + "\n")
                self.assertEqual(status, 2)
                self.assertEqual(output, "")
                self.assertIn("Record 1", error)
                self.assertNotIn("PRIVATE_TEXT", error)

    def test_empty_input_fails(self):
        for content, suffix in (("", ".jsonl"), ("\n", ".jsonl"), ("label,prediction\n", ".csv")):
            with self.subTest(suffix=suffix, content=content):
                status, output, error = self.invoke(content, suffix)
                self.assertEqual(status, 2)
                self.assertEqual(output, "")
                self.assertIn("at least one", error)

    def test_csv_requires_both_columns_and_values(self):
        for content in ("text\nalpha\n", "label,prediction\na,\n"):
            with self.subTest(content=content):
                status, output, _ = self.invoke(content, ".csv")
                self.assertEqual(status, 2)
                self.assertEqual(output, "")

    def test_valid_jsonl_and_numeric_zero(self):
        status, output, error = self.invoke(
            '{"label": 0, "prediction": 0}\n{"label": 1, "prediction": 0}\n'
        )
        self.assertEqual((status, error), (0, ""))
        report = json.loads(output)
        self.assertEqual(report["accuracy"], 0.5)
        self.assertEqual(report["labels"]["0"]["support"], 1)

    def test_custom_fields_in_csv(self):
        status, output, error = self.invoke(
            "truth,guess\na,a\nb,a\n",
            ".csv",
            ("--truth-field", "truth", "--prediction-field", "guess"),
        )
        self.assertEqual((status, error), (0, ""))
        self.assertEqual(json.loads(output)["accuracy"], 0.5)

    def test_later_invalid_record_produces_no_partial_score(self):
        status, output, error = self.invoke('{"label":"a","prediction":"a"}\n{"text":"alpha"}\n')
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("Record 2", error)


if __name__ == "__main__":
    unittest.main()
