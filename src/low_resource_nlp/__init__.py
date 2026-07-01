"""Low-resource NLP utilities for pre-processing, routing, labels, and evaluation."""

from ._version import __version__
from .audit import CodeSwitchAudit, LanguageSpan, TokenAudit, audit_code_switching
from .labels import (
    CANONICAL_EMOTIONS,
    EmotionMapping,
    label_to_valence_arousal,
    normalise_emotion_label,
    parse_label_va,
)
from .normalisation import NormalisationConfig, normalise_for_matching, normalise_text, tokenise_words
from .routing import LanguageProfile, LexicalLanguageRouter, RouteDecision

__all__ = [
    "CANONICAL_EMOTIONS",
    "CodeSwitchAudit",
    "EmotionMapping",
    "LanguageProfile",
    "LanguageSpan",
    "LexicalLanguageRouter",
    "NormalisationConfig",
    "RouteDecision",
    "TokenAudit",
    "audit_code_switching",
    "label_to_valence_arousal",
    "normalise_emotion_label",
    "normalise_for_matching",
    "normalise_text",
    "parse_label_va",
    "tokenise_words",
    "__version__",
]
