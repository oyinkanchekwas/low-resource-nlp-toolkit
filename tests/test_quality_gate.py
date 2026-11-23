import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.quality_gate import is_scannable


class QualityGateTests(unittest.TestCase):
    def test_excludes_private_benchmark_directory(self):
        self.assertFalse(is_scannable(Path(".benchmark-data/study/input.txt")))
        self.assertTrue(is_scannable(Path("docs/index.md")))

    def test_candidate_inside_private_directory_is_scanned(self):
        root = Path("/work/.benchmark-data/candidate")
        with patch("scripts.quality_gate.ROOT", root):
            self.assertTrue(is_scannable(root / "docs/index.md"))
            self.assertFalse(is_scannable(root / ".benchmark-data/private.txt"))


if __name__ == "__main__":
    unittest.main()
