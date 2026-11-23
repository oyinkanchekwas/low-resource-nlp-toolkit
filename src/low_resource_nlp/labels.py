"""Emotion label harmonisation for multilingual NLP experiments."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Mapping, Optional, Tuple


@dataclass(frozen=True)
class EmotionMapping:
    """A normalised emotion label and optional valence-arousal score."""

    original: str
    canonical: str
    valence: Optional[float]
    arousal: Optional[float]
    scale: Optional["RatingScale"] = None


@dataclass(frozen=True)
class RatingScale:
    """Bounds and description for a supplied set of dimensional ratings."""

    minimum: float
    maximum: float
    source: str
    perspective: str
    version: Optional[str] = None

    def __post_init__(self) -> None:
        for value in (self.minimum, self.maximum):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError("Scale bounds must be finite numbers.")
        if self.minimum >= self.maximum:
            raise ValueError("Scale minimum must be less than its maximum.")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (self.source, self.perspective)
        ):
            raise ValueError("A source and annotation perspective are required.")
        if self.version is not None and (
            not isinstance(self.version, str) or not self.version.strip()
        ):
            raise ValueError("Version must be a non-empty string when supplied.")


def normalise_emotion_label(label: str, *, aliases: Optional[Mapping[str, str]] = None) -> str:
    """Normalise spelling and apply explicitly supplied label mappings."""

    if not isinstance(label, str):
        raise TypeError("Label must be a string.")
    value = label.strip().lower().replace("_", " ").replace("-", " ")
    value = " ".join(value.split())
    if aliases is not None:
        if not isinstance(aliases, Mapping):
            raise TypeError("Aliases must be a mapping.")
        for key, target in aliases.items():
            if (
                not isinstance(key, str)
                or not key
                or not isinstance(target, str)
                or not target.strip()
            ):
                raise ValueError("Alias labels must be non-empty strings.")
            if key != " ".join(key.strip().lower().replace("_", " ").replace("-", " ").split()):
                raise ValueError("Alias keys must use normalised spelling.")
        value = aliases.get(value, value)
    return value


def parse_label_va(value: str) -> Optional[Tuple[float, float]]:
    """Parse a valence-arousal string such as `5.00#7.50`."""

    if not value or "#" not in value:
        return None
    left, right = value.split("#", 1)
    try:
        pair = float(left), float(right)
    except ValueError:
        return None
    if not all(math.isfinite(value) for value in pair):
        raise ValueError("Ratings must be finite numbers.")
    return pair


def label_to_valence_arousal(
    label: str,
    *,
    aliases: Optional[Mapping[str, str]] = None,
    coordinates: Optional[Mapping[str, Tuple[float, float]]] = None,
    scale: Optional[RatingScale] = None,
) -> EmotionMapping:
    """Return a label and ratings supplied for the declared scale."""

    if coordinates is not None and not isinstance(coordinates, Mapping):
        raise TypeError("Coordinates must be a mapping.")
    if scale is not None and not isinstance(scale, RatingScale):
        raise TypeError("Scale must be a RatingScale.")
    parsed = parse_label_va(label)
    if parsed:
        pair, canonical = parsed, "valence_arousal"
    else:
        canonical = normalise_emotion_label(label, aliases=aliases)
        pair = coordinates.get(canonical) if coordinates is not None else None
        if coordinates is not None and canonical in coordinates and pair is None:
            raise ValueError("A coordinate mapping must contain two ratings.")
    if pair is not None:
        if not isinstance(scale, RatingScale):
            raise ValueError("A rating scale is required for dimensional values.")
        if (
            not isinstance(pair, (tuple, list))
            or len(pair) != 2
            or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not scale.minimum <= value <= scale.maximum
                for value in pair
            )
        ):
            raise ValueError("Ratings must be finite numbers within the declared scale.")
        return EmotionMapping(label, canonical, pair[0], pair[1], scale)
    return EmotionMapping(label, canonical, None, None)


def map_emotion_sequence(
    labels: Iterable[str],
    *,
    aliases: Optional[Mapping[str, str]] = None,
    coordinates: Optional[Mapping[str, Tuple[float, float]]] = None,
    scale: Optional[RatingScale] = None,
) -> List[EmotionMapping]:
    """Apply the same label and rating configuration to a sequence."""

    return [
        label_to_valence_arousal(label, aliases=aliases, coordinates=coordinates, scale=scale)
        for label in labels
    ]
