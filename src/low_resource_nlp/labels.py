"""Emotion label harmonisation for multilingual NLP experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

CANONICAL_EMOTIONS = (
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
)

EMOTION_ALIASES: Dict[str, str] = {
    "angry": "anger",
    "annoyance": "anger",
    "annoyed": "anger",
    "anticipatory": "anticipation",
    "disgusted": "disgust",
    "fearful": "fear",
    "happy": "joy",
    "happiness": "joy",
    "sad": "sadness",
    "sad": "sadness",
    "positive sentiment": "positive",
    "negative sentiment": "negative",
    "none": "neutral",
    "other": "neutral",
}

VALENCE_AROUSAL: Dict[str, Tuple[float, float]] = {
    "anger": (2.5, 7.9),
    "anticipation": (6.5, 6.0),
    "disgust": (2.6, 5.8),
    "fear": (2.8, 7.4),
    "joy": (8.2, 7.6),
    "love": (8.4, 5.8),
    "negative": (2.5, 5.5),
    "neutral": (5.0, 5.0),
    "optimism": (7.5, 6.0),
    "positive": (7.5, 5.5),
    "sadness": (2.1, 3.4),
    "surprise": (7.0, 8.5),
    "trust": (7.5, 5.0),
}


@dataclass(frozen=True)
class EmotionMapping:
    """A normalised emotion label and optional valence-arousal score."""

    original: str
    canonical: str
    valence: Optional[float]
    arousal: Optional[float]


def normalise_emotion_label(label: str) -> str:
    """Map a raw emotion label to the canonical taxonomy."""

    value = (label or "").strip().lower().replace("_", " ").replace("-", " ")
    value = " ".join(value.split())
    value = EMOTION_ALIASES.get(value, value)
    if value in CANONICAL_EMOTIONS:
        return value
    return value


def parse_label_va(value: str) -> Optional[Tuple[float, float]]:
    """Parse a valence-arousal string such as `5.00#7.50`."""

    if not value or "#" not in value:
        return None
    left, right = value.split("#", 1)
    try:
        return float(left), float(right)
    except ValueError:
        return None


def label_to_valence_arousal(label: str) -> EmotionMapping:
    """Return canonical label and valence-arousal coordinates when known."""

    parsed = parse_label_va(label)
    if parsed:
        valence, arousal = parsed
        return EmotionMapping(label, "valence_arousal", valence, arousal)

    canonical = normalise_emotion_label(label)
    pair = VALENCE_AROUSAL.get(canonical)
    if pair:
        return EmotionMapping(label, canonical, pair[0], pair[1])
    return EmotionMapping(label, canonical, None, None)


def map_emotion_sequence(labels: Iterable[str]) -> List[EmotionMapping]:
    """Map a sequence of labels to canonical emotion mappings."""

    return [label_to_valence_arousal(label) for label in labels]
