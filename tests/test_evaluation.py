from __future__ import annotations

import unittest

from low_resource_nlp.evaluation import (
    accuracy,
    classification_report,
    confusion_matrix,
    selective_classification_report,
)


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

    def test_selective_report_separates_coverage_from_accuracy(self) -> None:
        report = selective_classification_report(
            ["yor", "yor", "hau", "hau"],
            ["yor", "eng", "hau", "eng"],
            [True, False, True, True],
            labels=["hau", "yor", "eng"],
        )

        self.assertEqual(report["accepted"], 3)
        self.assertEqual(report["coverage"], 0.75)
        self.assertEqual(report["selective_accuracy"], 0.6667)
        self.assertEqual(report["labels"]["yor"]["coverage"], 0.5)

    def test_selective_report_validates_lengths(self) -> None:
        with self.assertRaises(ValueError):
            selective_classification_report(["yor"], ["yor"], [])
        with self.assertRaises(ValueError):
            selective_classification_report(["yor"], ["yor"], ["false"])

    def test_absent_reference_group_has_undefined_coverage(self) -> None:
        report = selective_classification_report(["yor"], ["yor"], [True], ["yor", "hau"])
        self.assertIsNone(report["labels"]["hau"]["coverage"])
        self.assertIsNone(report["labels"]["hau"]["selective_accuracy"])

    def test_empty_selective_report_has_undefined_rates(self) -> None:
        report = selective_classification_report([], [], [])
        self.assertIsNone(report["coverage"])
        self.assertIsNone(report["overall_accuracy"])
        self.assertIsNone(report["selective_accuracy"])
        self.assertIsNone(report["accepted_macro_f1"])

    def test_selective_risk_is_unavailable_when_every_item_is_rejected(self) -> None:
        report = selective_classification_report(
            ["yor"],
            ["eng"],
            [False],
            labels=["yor", "eng"],
        )

        self.assertEqual(report["coverage"], 0.0)
        self.assertIsNone(report["selective_risk"])
        self.assertIsNone(report["selective_accuracy"])
        self.assertIsNone(report["labels"]["yor"]["selective_accuracy"])
        self.assertIsNone(report["accepted_macro_f1"])
        self.assertIsNone(report["accepted_weighted_f1"])


if __name__ == "__main__":
    unittest.main()
