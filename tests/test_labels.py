from __future__ import annotations

import unittest

from low_resource_nlp.labels import label_to_valence_arousal, normalise_emotion_label, parse_label_va


class LabelTests(unittest.TestCase):
    def test_alias_mapping(self) -> None:
        self.assertEqual(normalise_emotion_label("happy"), "joy")

    def test_valence_arousal_mapping(self) -> None:
        mapping = label_to_valence_arousal("joy")
        self.assertEqual(mapping.canonical, "joy")
        self.assertGreater(mapping.valence or 0, 8.0)

    def test_parse_label_va(self) -> None:
        self.assertEqual(parse_label_va("5.00#7.50"), (5.0, 7.5))

    def test_unknown_label_is_retained(self) -> None:
        mapping = label_to_valence_arousal("awe")
        self.assertEqual(mapping.canonical, "awe")
        self.assertIsNone(mapping.valence)


if __name__ == "__main__":
    unittest.main()
