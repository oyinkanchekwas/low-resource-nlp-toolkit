from __future__ import annotations

import unittest

from profile_fixture import test_router

from low_resource_nlp.audit import (
    UNDETERMINED,
    audit_token,
    iter_word_offsets,
)
from low_resource_nlp.audit import (
    audit_code_switching as configured_audit,
)
from low_resource_nlp.routing import LexicalLanguageRouter


def audit_code_switching(text, **kwargs):
    kwargs.setdefault("router", test_router())
    return configured_audit(text, **kwargs)


class CodeSwitchAuditTests(unittest.TestCase):
    def test_invalid_thresholds_are_rejected_even_for_empty_text(self) -> None:
        invalid = [float("nan"), float("inf"), float("-inf"), -0.1]
        for value in invalid + [1.1]:
            with self.subTest(setting="confidence", value=value), self.assertRaises(ValueError):
                audit_code_switching("", min_confidence=value)
        for value in invalid:
            with self.subTest(setting="margin", value=value), self.assertRaises(ValueError):
                audit_code_switching("", min_score_margin=value)

    def test_individual_token_rejects_invalid_thresholds(self) -> None:
        router = test_router()
        with self.assertRaises(ValueError):
            audit_token(
                "alpha", 0, 5, router=router, min_confidence=float("nan"), min_score_margin=0
            )
        with self.assertRaises(ValueError):
            audit_token(
                "alpha", 0, 5, router=router, min_confidence=0, min_score_margin=float("inf")
            )

    def test_finite_threshold_boundaries_are_accepted(self) -> None:
        for confidence in (0.0, 1.0):
            for margin in (0.0, 100.0):
                with self.subTest(confidence=confidence, margin=margin):
                    self.assertEqual(
                        audit_code_switching(
                            "alpha", min_confidence=confidence, min_score_margin=margin
                        ).token_count,
                        1,
                    )

    def test_iter_word_offsets_preserves_original_positions(self) -> None:
        tokens = iter_word_offsets("Ẹ xáàxọ̀, friend!")

        self.assertEqual(tokens[0], ("Ẹ", 0, 1))
        self.assertEqual(tokens[1], ("xáàxọ̀", 2, 8))
        self.assertEqual(tokens[2], ("friend", 10, 16))

    def test_audit_reports_evidence_from_two_profiles(self) -> None:
        report = audit_code_switching("amber acorn alpha check beta bravo output")

        self.assertEqual(report.dominant_language_code, "a")
        self.assertEqual(report.language_mix, {"a": 3, "b": 2})
        self.assertIn("mixed_language_signals", report.warnings)
        self.assertIn("high_code_switching", report.warnings)
        self.assertGreater(report.code_switch_ratio, 0)

    def test_audit_leaves_unsupported_text_unassigned(self) -> None:
        report = audit_code_switching("check")

        self.assertEqual(report.tokens[0].language_code, UNDETERMINED)
        self.assertEqual(report.tokens[0].accepted_language_code, UNDETERMINED)
        self.assertIn("no_supported_language_evidence", report.warnings)

    def test_unsupported_token_has_no_score(self) -> None:
        report = audit_code_switching("zzzxqqq")
        token = report.tokens[0]
        self.assertEqual(token.confidence, 0.0)
        self.assertFalse(any(token.signals.values()))
        self.assertEqual(token.accepted_language_code, UNDETERMINED)

    def test_span_mean_is_mean_of_relative_token_scores(self) -> None:
        report = audit_code_switching("beta bravo")
        self.assertEqual(len(report.spans), 1)
        expected = round(sum(token.confidence for token in report.tokens) / len(report.tokens), 4)
        self.assertEqual(report.spans[0].mean_confidence, expected)

    def test_audit_handles_empty_text(self) -> None:
        report = audit_code_switching("")

        self.assertEqual(report.dominant_language_code, UNDETERMINED)
        self.assertEqual(report.token_count, 0)
        self.assertEqual(report.warnings, ("empty_text",))

    def test_to_dict_contains_tokens_and_spans(self) -> None:
        payload = audit_code_switching("gamma").to_dict()

        self.assertEqual(payload["dominant_language_code"], "c")
        self.assertTrue(payload["tokens"])
        self.assertTrue(payload["spans"])

    def test_aggregate_report_uses_only_counts_and_ratio(self) -> None:
        text = "alpha @PRIVATE_MARKER"
        report = audit_code_switching(text)
        aggregate = report.to_aggregate_dict()
        self.assertEqual(
            set(aggregate),
            {
                "token_count",
                "routed_token_count",
                "accepted_token_count",
                "language_count",
                "code_switch_ratio",
            },
        )
        self.assertEqual(aggregate["token_count"], 1)
        self.assertEqual(aggregate["accepted_token_count"], 1)
        self.assertNotIn("PRIVATE_MARKER", str(aggregate))
        self.assertNotIn("alpha", str(aggregate))
        self.assertNotIn("tokens", aggregate)
        self.assertNotIn("spans", aggregate)
        self.assertNotIn("warnings", aggregate)

    def test_aggregate_does_not_return_custom_profile_names_or_codes(self) -> None:
        from low_resource_nlp.routing import LanguageProfile

        router = LexicalLanguageRouter(
            [LanguageProfile("PRIVATE_CODE", "PRIVATE_NAME", keywords=("alpha",))]
        )
        aggregate = audit_code_switching("alpha", router=router).to_aggregate_dict()
        self.assertNotIn("PRIVATE", str(aggregate))

    def test_links_and_usernames_are_not_token_evidence(self) -> None:
        for text in (
            "https://alpha.example.org",
            "www.alpha.example.org",
            "@alpha",
            "https&#58;&#47;&#47;alpha.example.org",
            "&#64;alpha",
            "&commat;alpha",
            "@e\u0301alpha",
            "HTTPS://alpha.example.org",
            "https://@alpha.example.org",
        ):
            with self.subTest(text=text):
                report = audit_code_switching(text)
                self.assertEqual(report.text, text)
                self.assertEqual(report.token_count, 0)
                self.assertEqual(report.accepted_token_count, 0)
                self.assertEqual(report.dominant_language_code, UNDETERMINED)
                self.assertEqual(report.warnings, ("no_auditable_tokens",))
                self.assertEqual(report.spans, ())

    def test_surrounding_tokens_keep_original_offsets(self) -> None:
        text = "Ẹ alpha @alpha beta https&#58;//alpha.example.org alpha"
        report = audit_code_switching(text)
        self.assertEqual([token.text for token in report.tokens], ["Ẹ", "alpha", "beta", "alpha"])
        for token in report.tokens:
            self.assertEqual(text[token.start : token.end], token.text)
        for span in report.spans:
            self.assertEqual(text[span.start : span.end], span.text)
            self.assertNotIn("@alpha", span.text)
            self.assertNotIn("https", span.text)

    def test_ignored_items_split_otherwise_matching_spans(self) -> None:
        for separator in (
            " @alpha ",
            " https://alpha.example.org ",
            " &#64;alpha ",
            "&nbsp;@alpha ",
        ):
            with self.subTest(separator=separator):
                report = audit_code_switching("alpha" + separator + "alpha")
                self.assertEqual([token.text for token in report.tokens], ["alpha", "alpha"])
                self.assertEqual([span.text for span in report.spans], ["alpha", "alpha"])

    def test_word_adjacent_to_link_is_preserved(self) -> None:
        text = "alphahttps://alpha.example.org"
        report = audit_code_switching(text)
        self.assertEqual([token.text for token in report.tokens], ["alpha"])
        self.assertEqual((report.tokens[0].start, report.tokens[0].end), (0, 5))

    def test_encoded_whitespace_does_not_become_language_evidence(self) -> None:
        report = audit_code_switching("@alpha&nbsp;alpha")
        self.assertEqual([token.text for token in report.tokens], ["alpha"])

    def test_multiple_ignored_items_preserve_surrounding_language_mix(self) -> None:
        baseline = audit_code_switching("alpha alpha")
        report = audit_code_switching("alpha @beta https://beta.example.org alpha")
        self.assertEqual(report.language_mix, baseline.language_mix)
        self.assertEqual(report.code_switch_ratio, baseline.code_switch_ratio)
        self.assertEqual(report.accepted_token_count, baseline.accepted_token_count)

    def test_repeated_ignored_items_do_not_change_offsets(self) -> None:
        text = ("alpha @alpha " * 500).strip()
        report = audit_code_switching(text)
        self.assertEqual(report.token_count, 500)
        self.assertEqual(len(report.spans), 500)
        self.assertTrue(all(text[token.start : token.end] == "alpha" for token in report.tokens))

    def test_unrecognised_reference_remains_normal_input(self) -> None:
        text = "alpha &unknownname; alpha"
        report = audit_code_switching(text)
        self.assertEqual(
            [(item.text, item.start, item.end) for item in report.tokens], iter_word_offsets(text)
        )

    def test_username_boundary_respects_unicode_normalisation(self) -> None:
        joined = audit_code_switching("a\u0301@alpha")
        separated = audit_code_switching("é\u0301@alpha")
        self.assertEqual([item.text for item in joined.tokens], ["a\u0301", "alpha"])
        self.assertEqual([item.text for item in separated.tokens], ["é\u0301"])

    def test_plain_text_tokenisation_is_unchanged(self) -> None:
        text = "Ẹ xáàxọ̀, alpha!"
        report = audit_code_switching(text)
        self.assertEqual(
            [(token.text, token.start, token.end) for token in report.tokens],
            iter_word_offsets(text),
        )

    def test_unicode_and_punctuation_keep_original_offsets(self) -> None:
        cases = [
            ("Ẹ xáàxọ̀, alpha!", ["Ẹ", "xáàxọ̀", "alpha"]),
            (
                "E\u0323 ka\u0301a\u0300ro\u0323\u0300, alpha!",
                ["E\u0323", "ka\u0301a\u0300ro\u0323\u0300", "alpha"],
            ),
            ("alpha😀ẹ xáàxọ̀!", ["alpha", "ẹ", "xáàxọ̀"]),
            ("(alpha)...[ẹ] / xáàxọ̀", ["alpha", "ẹ", "xáàxọ̀"]),
            ("Ẹ @someone😀alpha https://example.org/path! xáàxọ̀", ["Ẹ", "alpha", "xáàxọ̀"]),
            ("😀@someone, alpha &amp; xáàxọ̀", ["alpha", "xáàxọ̀"]),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                report = audit_code_switching(text)
                self.assertEqual([token.text for token in report.tokens], expected)
                for item in (*report.tokens, *report.spans):
                    self.assertEqual(text[item.start : item.end], item.text)
                    self.assertLess(item.start, item.end)


if __name__ == "__main__":
    unittest.main()
