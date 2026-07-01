from __future__ import annotations

import unittest

from low_resource_nlp.audit import (
    AMBIGUOUS,
    UNDETERMINED,
    audit_code_switching,
    iter_word_offsets,
)


class CodeSwitchAuditTests(unittest.TestCase):
    def test_iter_word_offsets_preserves_original_positions(self) -> None:
        tokens = iter_word_offsets("Ẹ káàrọ̀, friend!")

        self.assertEqual(tokens[0], ("Ẹ", 0, 1))
        self.assertEqual(tokens[1], ("káàrọ̀", 2, 8))
        self.assertEqual(tokens[2], ("friend", 10, 16))

    def test_audit_reports_mixed_pidgin_and_english_evidence(self) -> None:
        report = audit_code_switching("abeg make una check this model output")

        self.assertEqual(report.dominant_language_code, "pcm")
        self.assertEqual(report.language_mix, {"eng": 2, "pcm": 3})
        self.assertIn("mixed_language_signals", report.warnings)
        self.assertIn("high_code_switching", report.warnings)
        self.assertGreater(report.code_switch_ratio, 0)

    def test_audit_abstains_on_weak_ascii_guess(self) -> None:
        report = audit_code_switching("check")

        self.assertEqual(report.tokens[0].language_code, "eng")
        self.assertEqual(report.tokens[0].accepted_language_code, AMBIGUOUS)
        self.assertIn("no_supported_language_evidence", report.warnings)

    def test_audit_handles_empty_text(self) -> None:
        report = audit_code_switching("")

        self.assertEqual(report.dominant_language_code, UNDETERMINED)
        self.assertEqual(report.token_count, 0)
        self.assertEqual(report.warnings, ("empty_text",))

    def test_to_dict_contains_tokens_and_spans(self) -> None:
        payload = audit_code_switching("sannu ina lafiya").to_dict()

        self.assertEqual(payload["dominant_language_code"], "hau")
        self.assertTrue(payload["tokens"])
        self.assertTrue(payload["spans"])


if __name__ == "__main__":
    unittest.main()
