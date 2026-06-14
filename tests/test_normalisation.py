from __future__ import annotations

import unittest

from low_resource_nlp.normalisation import (
    NormalisationConfig,
    normalise_for_matching,
    normalise_text,
    tokenise_words,
)


class NormalisationTests(unittest.TestCase):
    def test_normalise_preserves_yoruba_diacritics_by_default(self) -> None:
        self.assertIn("ẹ", normalise_text("Ẹ káàrọ̀!!!"))

    def test_normalise_for_matching_strips_diacritics(self) -> None:
        self.assertEqual(normalise_for_matching("Ẹ káàrọ̀"), "e kaaro")

    def test_url_user_and_hashtag_handling(self) -> None:
        text = normalise_text("Visit https://example.com @user #LowResourceNLP")
        self.assertEqual(text, "visit <url> <user> low resource nlp")

    def test_repeated_characters_are_limited(self) -> None:
        config = NormalisationConfig(repeated_char_limit=2)
        self.assertEqual(normalise_text("soooo good", config), "soo good")

    def test_tokenise_unicode_words(self) -> None:
        self.assertEqual(tokenise_words("Ẹ káàrọ̀, friend!"), ["ẹ", "káàrọ̀", "friend"])


if __name__ == "__main__":
    unittest.main()
