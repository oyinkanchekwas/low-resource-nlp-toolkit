import contextlib
import hashlib
import io
import json
import shlex
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from profile_fixture import PROFILE_DATA

from benchmarks.afrisenti import run_benchmark as benchmark


def predictions():
    return [
        benchmark.RoutingPrediction(code, code, 1.0, 2.0, code, 1.0, 2.0)
        for code in benchmark.LANGUAGES
    ]


class BenchmarkConfigurationTests(unittest.TestCase):
    def make_profiles(self, root):
        path = root / "profiles.json"
        path.write_text(json.dumps(PROFILE_DATA), encoding="utf-8")
        return path

    def execute(self, root, profiles, extra=()):
        with (
            patch.object(benchmark, "ROOT", root),
            patch.object(benchmark, "prepare_data") as prepare,
            patch.object(benchmark, "load_predictions", return_value=predictions()),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            status = benchmark.main(["--profiles", str(profiles), *extra])
        return status, prepare

    def test_default_outputs_preserve_historical_files_and_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiles = self.make_profiles(root)
            historical = [root / "docs/benchmark.md", root / "reports/afrisenti-routing.json"]
            for path in historical:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("preserved", encoding="utf-8")
            for _ in range(2):
                status, prepare = self.execute(root, profiles)
                self.assertEqual(status, 0)
                self.assertFalse(prepare.call_args.args[2])
            reports = sorted((root / ".benchmark-data/afrisenti-runs").glob("*/report.json"))
            self.assertEqual(len(reports), 2)
            for path in historical:
                self.assertEqual(path.read_text(), "preserved")
            report = json.loads(reports[0].read_text())
            digest = hashlib.sha256(profiles.read_bytes()).hexdigest()
            self.assertEqual(report["profiles"], {"sha256": digest})
            self.assertEqual(report["schema_version"], 2)
            rendered = reports[0].with_suffix(".md").read_text()
            self.assertIn(digest, rendered)
            command = next(line for line in rendered.splitlines() if line.startswith("PYTHONPATH="))
            args = benchmark.build_parser().parse_args(shlex.split(command)[3:])
            self.assertEqual(args.profiles, Path("profiles.json"))
            self.assertEqual(args.target_accuracy, 0.9)
            self.assertEqual(args.json_output, Path("benchmark-output/report.json"))
            self.assertIsNotNone(args.markdown_output)
            self.assertFalse(args.download)

    def test_report_requires_a_valid_profile_digest(self):
        for digest in ("", "unknown", "0" * 63):
            with self.subTest(digest=digest), self.assertRaises(ValueError):
                benchmark.build_report(
                    benchmark.read_manifest(),
                    predictions(),
                    predictions(),
                    0.9,
                    profile_sha256=digest,
                )

    def test_explicit_existing_output_is_rejected_before_data_access(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiles = self.make_profiles(root)
            target = root / "existing.json"
            target.write_text("preserved")
            with (
                patch.object(benchmark, "prepare_data") as prepare,
                contextlib.redirect_stderr(io.StringIO()),
            ):
                with self.assertRaises(SystemExit) as exc:
                    benchmark.main(["--profiles", str(profiles), "--json-output", str(target)])
            self.assertEqual(exc.exception.code, 2)
            prepare.assert_not_called()
            self.assertEqual(target.read_text(), "preserved")

    def test_invalid_profile_is_rejected_before_data_access(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiles = root / "invalid.json"
            profiles.write_text("{}")
            with patch.object(benchmark, "prepare_data") as prepare:
                with self.assertRaises(ValueError):
                    benchmark.main(["--profiles", str(profiles)])
            prepare.assert_not_called()

    def test_same_output_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiles = self.make_profiles(root)
            target = root / "report"
            with (
                patch.object(benchmark, "prepare_data") as prepare,
                contextlib.redirect_stderr(io.StringIO()),
            ):
                with self.assertRaises(SystemExit):
                    benchmark.main(
                        [
                            "--profiles",
                            str(profiles),
                            "--json-output",
                            str(target),
                            "--markdown-output",
                            str(target),
                        ]
                    )
            prepare.assert_not_called()

    def test_unaccepted_test_predictions_render_without_a_numeric_accuracy(self):
        report = benchmark.build_report(
            benchmark.read_manifest(),
            predictions(),
            [
                benchmark.RoutingPrediction(code, "und", 0.0, 0.0, "und", 0.0, 0.0)
                for code in benchmark.LANGUAGES
            ],
            0.9,
            profile_sha256="0" * 64,
        )
        self.assertIsNone(report["test"]["selected_policy"]["selective_accuracy"])
        self.assertIn("N/A", benchmark.render_markdown(report))


if __name__ == "__main__":
    unittest.main()
