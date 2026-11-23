import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def run_example(self, filename, text):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "examples" / filename),
                text,
                "--profiles",
                str(ROOT / "examples" / "profiles.json"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_route_example(self):
        result = self.run_example("route_texts.py", "alpha amber")
        self.assertEqual(result["accepted_language"], "a")

    def test_audit_example(self):
        result = self.run_example("audit_code_switching.py", "alpha beta")
        self.assertEqual(result["token_count"], 2)
        self.assertNotIn("text", result)


if __name__ == "__main__":
    unittest.main()
