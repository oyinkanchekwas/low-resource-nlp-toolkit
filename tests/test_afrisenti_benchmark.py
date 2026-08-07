from __future__ import annotations

import hashlib
import re
import tempfile
import unittest
from pathlib import Path

from benchmarks.afrisenti.run_benchmark import (
    RoutingPrediction,
    choose_policy,
    read_manifest,
    verify_file,
    wilson_interval,
)


def _prediction(
    truth: str,
    prediction: str,
    *,
    confidence: float,
    margin: float,
) -> RoutingPrediction:
    return RoutingPrediction(
        truth=truth,
        prediction=prediction,
        confidence=confidence,
        score_margin=margin,
        stripped_prediction=prediction,
        stripped_confidence=confidence,
        stripped_score_margin=margin,
    )


class AfriSentiBenchmarkTests(unittest.TestCase):
    def test_manifest_pins_both_splits_for_each_language(self) -> None:
        manifest = read_manifest()
        files = manifest["files"]

        self.assertEqual(
            {(entry["language"], entry["split"]) for entry in files},
            {
                (language, split)
                for language in ("hau", "ibo", "pcm", "swa", "yor")
                for split in ("development", "test")
            },
        )
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) for entry in files))

    def test_policy_selection_maximises_qualifying_coverage(self) -> None:
        predictions = [
            _prediction("yor", "yor", confidence=0.9, margin=2.0),
            _prediction("hau", "hau", confidence=0.8, margin=1.0),
            _prediction("ibo", "eng", confidence=0.4, margin=0.2),
        ]

        policy = choose_policy(
            predictions,
            target_accuracy=1.0,
            confidence_grid=[0.0, 0.5],
            margin_grid=[0.0, 0.5],
        )

        self.assertEqual(policy["accepted"], 2)
        self.assertEqual(policy["coverage"], 0.6667)
        self.assertEqual(policy["min_confidence"], 0.0)
        self.assertEqual(policy["min_score_margin"], 0.5)

    def test_verify_file_rejects_changed_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.tsv"
            path.write_text("ID\ttweet\n1\thello\n", encoding="utf-8")
            expected = hashlib.sha256(path.read_bytes()).hexdigest()

            verify_file(path, expected)
            with self.assertRaises(ValueError):
                verify_file(path, "0" * 64)

    def test_wilson_interval_contains_observed_proportion(self) -> None:
        lower, upper = wilson_interval(90, 100)

        self.assertLess(lower, 0.9)
        self.assertGreater(upper, 0.9)


if __name__ == "__main__":
    unittest.main()
