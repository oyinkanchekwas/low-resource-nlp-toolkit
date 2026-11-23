from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from profile_fixture import PROFILE_DATA

from low_resource_nlp import __version__
from low_resource_nlp.cli import main


class CliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.profiles = Path(self.directory.name) / "profiles.json"
        self.profiles.write_text(json.dumps(PROFILE_DATA), encoding="utf-8")

    def run_cli(self, args):
        if args and args[0] in {"route", "audit"}:
            args = args + ["--profiles", str(self.profiles)]
        return main(args)

    def test_version_command_outputs_package_version(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            with self.assertRaises(SystemExit) as exc:
                self.run_cli(["--version"])

        self.assertEqual(exc.exception.code, 0)
        self.assertIn(f"low-resource-nlp {__version__}", buffer.getvalue())

    def test_route_command_outputs_json(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = self.run_cli(["route", "alpha amber"])

        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["language_code"], "a")
        self.assertTrue(payload["accepted"])
        self.assertGreater(payload["score_margin"], 0)

    def test_route_command_can_abstain(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = self.run_cli(["route", "check", "--min-score-margin", "0.75"])

        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["abstention_reason"], "undetermined")

    def test_audit_command_outputs_code_switch_report(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = self.run_cli(["audit", "alpha amber acorn beta bravo"])

        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["dominant_language_code"], "a")
        self.assertIn("mixed_language_signals", payload["warnings"])
        self.assertTrue(payload["tokens"])
        self.assertTrue(payload["spans"])

    def test_label_command_outputs_mapping(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = main(["label", "happy"])

        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["canonical"], "happy")
        self.assertIsNone(payload["valence"])
        self.assertIsNone(payload["scale"])

    def test_label_command_reads_ratings_with_scale(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = main(
                [
                    "label",
                    "0.5#0.7",
                    "--scale-min",
                    "0",
                    "--scale-max",
                    "1",
                    "--source",
                    "study A",
                    "--perspective",
                    "reader",
                ]
            )
        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["scale"]["perspective"], "reader")
        self.assertEqual(payload["valence"], 0.5)

    def test_label_command_requires_scale_for_ratings(self) -> None:
        with self.assertRaises(SystemExit):
            main(["label", "0.5#0.7"])


if __name__ == "__main__":
    unittest.main()
