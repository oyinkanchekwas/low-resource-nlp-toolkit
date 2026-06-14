from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from low_resource_nlp.cli import main


class CliTests(unittest.TestCase):
    def test_route_command_outputs_json(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = main(["route", "abeg make una check am"])

        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["language_code"], "pcm")

    def test_label_command_outputs_mapping(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            status = main(["label", "happy"])

        payload = json.loads(buffer.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["canonical"], "joy")


if __name__ == "__main__":
    unittest.main()
