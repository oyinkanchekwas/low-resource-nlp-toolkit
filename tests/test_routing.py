from __future__ import annotations

import unittest

from low_resource_nlp.routing import LexicalLanguageRouter, character_ngrams, softmax_scores


class RoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = LexicalLanguageRouter.default()

    def test_routes_yoruba_with_diacritic_signal(self) -> None:
        decision = self.router.route("Ẹ káàrọ̀, báwo ni?")
        self.assertEqual(decision.language_code, "yor")
        self.assertGreater(decision.confidence, 0)

    def test_routes_pidgin_with_lexical_signal(self) -> None:
        decision = self.router.route("abeg make una help me check am")
        self.assertEqual(decision.language_code, "pcm")

    def test_routes_swahili(self) -> None:
        decision = self.router.route("asante sana kwa msaada wako")
        self.assertEqual(decision.language_code, "swa")

    def test_undetermined_for_empty_text(self) -> None:
        decision = self.router.route("")
        self.assertEqual(decision.language_code, "und")

    def test_character_ngrams(self) -> None:
        self.assertEqual(character_ngrams("abcd", 3), ["abc", "bcd"])

    def test_softmax_scores(self) -> None:
        scores = softmax_scores({"a": 1.0, "b": 2.0})
        self.assertAlmostEqual(sum(scores.values()), 1.0)


if __name__ == "__main__":
    unittest.main()
