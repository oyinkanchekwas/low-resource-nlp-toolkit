from __future__ import annotations

import unittest

from low_resource_nlp.labels import (
    RatingScale,
    label_to_valence_arousal,
    map_emotion_sequence,
    normalise_emotion_label,
    parse_label_va,
)


class LabelTests(unittest.TestCase):
    def test_alias_mapping(self) -> None:
        self.assertEqual(normalise_emotion_label("happy"), "happy")
        self.assertEqual(normalise_emotion_label("happy", aliases={"happy": "joy"}), "joy")

    def test_valence_arousal_mapping(self) -> None:
        mapping = label_to_valence_arousal("joy")
        self.assertEqual(mapping.canonical, "joy")
        self.assertIsNone(mapping.valence)
        self.assertIsNone(mapping.arousal)
        self.assertIsNone(mapping.scale)

    def test_parse_label_va(self) -> None:
        self.assertEqual(parse_label_va("5.00#7.50"), (5.0, 7.5))

    def test_unknown_label_is_retained(self) -> None:
        mapping = label_to_valence_arousal("awe")
        self.assertEqual(mapping.canonical, "awe")
        self.assertIsNone(mapping.valence)

    def test_other_none_and_neutral_remain_distinct(self) -> None:
        self.assertEqual(
            [normalise_emotion_label(x) for x in ("other", "none", "neutral")],
            ["other", "none", "neutral"],
        )
        self.assertEqual(normalise_emotion_label("other", aliases={"other": "neutral"}), "neutral")

    def test_categories_do_not_receive_default_ratings(self) -> None:
        for label in (
            "anger",
            "anticipation",
            "disgust",
            "fear",
            "joy",
            "love",
            "negative",
            "neutral",
            "optimism",
            "positive",
            "sadness",
            "surprise",
            "trust",
        ):
            with self.subTest(label=label):
                result = label_to_valence_arousal(label)
                self.assertEqual(result.canonical, label)
                self.assertIsNone(result.valence)
                self.assertIsNone(result.arousal)

    def test_automatic_aliases_are_not_applied(self) -> None:
        for label in ("angry", "annoyance", "happy", "happiness", "sad"):
            with self.subTest(label=label):
                self.assertEqual(normalise_emotion_label(label), label)

    def test_supplied_coordinates_and_metadata(self) -> None:
        scale = RatingScale(0, 1, source="study A", perspective="reader", version="1")
        mapping = label_to_valence_arousal(
            "happy", aliases={"happy": "joy"}, coordinates={"joy": (0.7, 0.4)}, scale=scale
        )
        self.assertEqual(
            (mapping.original, mapping.canonical, mapping.valence, mapping.arousal),
            ("happy", "joy", 0.7, 0.4),
        )
        self.assertEqual(mapping.scale, scale)

    def test_numeric_input_requires_scale_and_retains_details(self) -> None:
        with self.assertRaises(ValueError):
            label_to_valence_arousal("0.5#0.7")
        scale = RatingScale(0, 1, source="study A", perspective="writer")
        result = label_to_valence_arousal("0.5#0.7", scale=scale)
        self.assertEqual((result.valence, result.arousal, result.scale), (0.5, 0.7, scale))

    def test_invalid_bounds_metadata_and_ratings(self) -> None:
        for args in (
            (0, 0, "source", "reader"),
            (float("nan"), 1, "source", "reader"),
            (0, 1, "", "reader"),
            (0, 1, "source", ""),
            (True, 1, "source", "reader"),
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                RatingScale(*args)
        scale = RatingScale(0, 1, source="study A", perspective="reader")
        for value in ("nan#0.5", "inf#0.5", "1.1#0.5", "-0.1#0.5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                label_to_valence_arousal(value, scale=scale)
        for pair in ((float("inf"), 0), (True, 0), (0, 2), (0,)):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                label_to_valence_arousal("joy", coordinates={"joy": pair}, scale=scale)

    def test_invalid_mapping_inputs_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            normalise_emotion_label("joy", aliases=[("joy", "happy")])
        with self.assertRaises(TypeError):
            label_to_valence_arousal("joy", coordinates=[])
        with self.assertRaises(TypeError):
            label_to_valence_arousal("joy", scale="unknown")
        with self.assertRaises(ValueError):
            label_to_valence_arousal("joy", coordinates={"joy": None})

    def test_sequence_uses_explicit_mapping(self) -> None:
        scale = RatingScale(1, 9, source="study A", perspective="reader")
        results = map_emotion_sequence(
            ["happy", "other"], aliases={"happy": "joy"}, coordinates={"joy": (7, 6)}, scale=scale
        )
        self.assertEqual((results[0].canonical, results[0].valence), ("joy", 7))
        self.assertEqual((results[1].canonical, results[1].valence), ("other", None))


if __name__ == "__main__":
    unittest.main()
