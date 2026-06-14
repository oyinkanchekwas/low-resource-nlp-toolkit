from __future__ import annotations

import unittest

from low_resource_nlp.evaluation import accuracy, classification_report, confusion_matrix


class EvaluationTests(unittest.TestCase):
    def test_accuracy(self) -> None:
        self.assertEqual(accuracy(["a", "b", "b"], ["a", "a", "b"]), 0.6667)

    def test_confusion_matrix(self) -> None:
        matrix = confusion_matrix(["joy", "sadness"], ["joy", "joy"])
        self.assertEqual(matrix["joy"]["joy"], 1)
        self.assertEqual(matrix["sadness"]["joy"], 1)

    def test_classification_report(self) -> None:
        report = classification_report(["joy", "sadness", "joy"], ["joy", "joy", "joy"])
        self.assertIn("macro_f1", report)
        self.assertEqual(report["labels"]["joy"]["support"], 2)


if __name__ == "__main__":
    unittest.main()
