from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from low_resource_nlp import __version__
from low_resource_nlp.cli import main


class CliTests(unittest.TestCase):
    def test_version_command_outputs_package_version(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            with self.assertRaises(SystemExit) as exc:
                main(["--version"])

        self.assertEqual(exc.exception.code, 0)
        self.assertIn(f"low-resource-nlp {__version__}", buffer.getvalue())

    def test_route_command_outputs_json(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = main(["route", "abeg make una check am"])

        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["language_code"], "pcm")

    def test_audit_command_outputs_code_switch_report(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = main(["audit", "abeg make una check this model output"])

        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["dominant_language_code"], "pcm")
        self.assertIn("mixed_language_signals", payload["warnings"])
        self.assertTrue(payload["tokens"])
        self.assertTrue(payload["spans"])

    def test_label_command_outputs_mapping(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = main(["label", "happy"])

        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["canonical"], "joy")


if __name__ == "__main__":
    unittest.main()
