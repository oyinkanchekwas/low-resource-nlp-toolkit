from __future__ import annotations

import unittest

from profile_fixture import test_router

from low_resource_nlp.routing import (
    character_ngrams,
    score_margin,
    softmax_scores,
)


class RoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = test_router()

    def test_routes_with_character_signal(self) -> None:
        decision = self.router.route("ẹ alpha")
        self.assertEqual(decision.language_code, "a")
        self.assertGreater(decision.confidence, 0)

    def test_routes_with_lexical_signal(self) -> None:
        decision = self.router.route("alpha amber acorn")
        self.assertEqual(decision.language_code, "a")

    def test_routes_second_profile(self) -> None:
        decision = self.router.route("beta bravo")
        self.assertEqual(decision.language_code, "b")

    def test_undetermined_for_empty_text(self) -> None:
        decision = self.router.route("")
        self.assertEqual(decision.language_code, "und")

    def test_links_and_usernames_do_not_supply_routing_evidence(self) -> None:
        for text in (
            "https://alpha.example.org",
            "www.alpha.example.org",
            "@alpha",
            "https&#58;&#47;&#47;alpha.example.org",
            "&#64;alpha",
            "123 ...",
        ):
            with self.subTest(text=text):
                self.assertEqual(self.router.route(text).language_code, "und")

    def test_links_do_not_change_surrounding_text_scores(self) -> None:
        baseline = self.router.route("alpha amber")
        with_links = self.router.route("alpha @beta https://beta.example.org amber")
        self.assertEqual(with_links.scores, baseline.scores)
        self.assertEqual(with_links.signals, baseline.signals)

    def test_character_ngrams(self) -> None:
        self.assertEqual(character_ngrams("abcd", 3), ["abc", "bcd"])

    def test_softmax_scores(self) -> None:
        scores = softmax_scores({"a": 1.0, "b": 2.0})
        self.assertAlmostEqual(sum(scores.values()), 1.0)

    def test_score_margin_uses_two_strongest_positive_scores(self) -> None:
        self.assertEqual(score_margin({"a": 2.5, "b": 1.0, "c": 0.0}), 1.5)

    def test_selective_route_accepts_strong_evidence(self) -> None:
        result = self.router.route_selectively(
            "ẹ alpha",
            min_score_margin=0.75,
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.accepted_language_code, "a")
        self.assertIsNone(result.abstention_reason)

    def test_selective_route_abstains_on_narrow_margin(self) -> None:
        result = self.router.route_selectively("check", min_score_margin=0.75)

        self.assertFalse(result.accepted)
        self.assertIsNone(result.accepted_language_code)
        self.assertEqual(result.abstention_reason, "undetermined")

    def test_selective_route_validates_thresholds(self) -> None:
        with self.assertRaises(ValueError):
            self.router.route_selectively("text", min_confidence=1.1)
        with self.assertRaises(ValueError):
            self.router.route_selectively("text", min_score_margin=-0.1)
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.router.route_selectively("text", min_score_margin=value)


if __name__ == "__main__":
    unittest.main()
