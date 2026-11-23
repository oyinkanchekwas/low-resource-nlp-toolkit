"""Lightweight language and dialect routing for low-resource NLP."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .normalisation import (
    NormalisationConfig,
    normalise_for_matching,
    normalise_text,
    tokenise_words,
)

_ROUTING_NORMALISATION = NormalisationConfig(url_replacement=" ", user_replacement=" ")
_ROUTING_MATCH_NORMALISATION = NormalisationConfig(
    preserve_diacritics=False, url_replacement=" ", user_replacement=" "
)


@dataclass(frozen=True)
class LanguageProfile:
    """Lexical profile for a language or dialect route."""

    code: str
    name: str
    stopwords: Tuple[str, ...] = ()
    keywords: Tuple[str, ...] = ()
    unique_chars: Tuple[str, ...] = ()
    aliases: Tuple[str, ...] = ()


@dataclass(frozen=True)
class RouteDecision:
    """Routing result returned by `LexicalLanguageRouter`."""

    language_code: str
    language_name: str
    confidence: float
    scores: Mapping[str, float]
    signals: Mapping[str, List[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class SelectiveRouteDecision:
    """A route together with the decision to accept it or abstain."""

    decision: RouteDecision
    accepted: bool
    accepted_language_code: str | None
    accepted_language_name: str | None
    score_margin: float
    abstention_reason: str | None


def load_profiles(path: str | Path) -> List[LanguageProfile]:
    """Read a JSON profile collection with a source description."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"source", "profiles"}:
        raise ValueError("Profile files require source and profiles fields.")
    if not isinstance(data["source"], str) or not data["source"].strip():
        raise ValueError("A profile source description is required.")
    if not isinstance(data["profiles"], list) or not data["profiles"]:
        raise ValueError("Profiles must be a non-empty list.")
    allowed = {"code", "name", "keywords", "stopwords", "unique_chars", "aliases"}
    profiles = []
    for item in data["profiles"]:
        if not isinstance(item, dict) or set(item) - allowed or not {"code", "name"} <= set(item):
            raise ValueError(
                "Each profile requires code and name, with recognised evidence fields."
            )
        fields = dict(item)
        for field_name in ("keywords", "stopwords", "unique_chars", "aliases"):
            value = fields.get(field_name, [])
            if not isinstance(value, list) or any(
                not isinstance(x, str) or not x.strip() for x in value
            ):
                raise ValueError("Profile evidence must be lists of non-empty strings.")
            fields[field_name] = tuple(value)
        profiles.append(LanguageProfile(**fields))
    LexicalLanguageRouter(profiles)
    return profiles


def character_ngrams(text: str, n: int = 3) -> List[str]:
    """Create character n-grams for compact lexical matching."""

    collapsed = normalise_for_matching(text).replace(" ", "_")
    if len(collapsed) < n:
        return [collapsed] if collapsed else []
    return [collapsed[index : index + n] for index in range(len(collapsed) - n + 1)]


def score_margin(scores: Mapping[str, float]) -> float:
    """Return the gap between the two strongest positive routing scores."""

    positive = sorted((score for score in scores.values() if score > 0), reverse=True)
    if not positive:
        return 0.0
    if len(positive) == 1:
        return round(positive[0], 4)
    return round(positive[0] - positive[1], 4)


class LexicalLanguageRouter:
    """Dependency-light router using script, lexical, and character signals."""

    def __init__(self, profiles: Sequence[LanguageProfile]):
        self.profiles = list(profiles)
        if not self.profiles or any(not isinstance(p, LanguageProfile) for p in self.profiles):
            raise ValueError("Supply at least one LanguageProfile.")
        codes = []
        for profile in self.profiles:
            if any(
                not isinstance(value, str) or not value.strip()
                for value in (profile.code, profile.name)
            ):
                raise ValueError("Profile code and name must be non-empty strings.")
            if profile.code in {"und", "ambiguous"}:
                raise ValueError("Profile code is reserved.")
            for values in (
                profile.keywords,
                profile.stopwords,
                profile.unique_chars,
                profile.aliases,
            ):
                if not isinstance(values, (tuple, list)) or any(
                    not isinstance(x, str) or not x.strip() for x in values
                ):
                    raise ValueError("Profile evidence must contain non-empty strings.")
            if not (profile.keywords or profile.stopwords or profile.unique_chars):
                raise ValueError("Each profile requires lexical or character evidence.")
            codes.append(profile.code)
        if len(set(codes)) != len(codes):
            raise ValueError("Profile codes must be distinct.")
        self.profile_by_code = {profile.code: profile for profile in self.profiles}
        self._keyword_index = {
            profile.code: {normalise_for_matching(word) for word in profile.keywords}
            for profile in self.profiles
        }
        self._stopword_index = {
            profile.code: {normalise_for_matching(word) for word in profile.stopwords}
            for profile in self.profiles
        }
        self._char_index = {
            profile.code: {normalise_for_matching(char) for char in profile.unique_chars}
            for profile in self.profiles
        }

    @classmethod
    def default(cls) -> "LexicalLanguageRouter":
        """Require explicit profiles when migrating older callers."""

        raise ValueError("Supply profiles with LexicalLanguageRouter(load_profiles(path)).")

    def route(self, text: str) -> RouteDecision:
        """Route a text to the most likely language profile."""

        normalised = normalise_text(text, _ROUTING_NORMALISATION)
        match_text = normalise_text(text, _ROUTING_MATCH_NORMALISATION)
        tokens = tokenise_words(match_text)
        if not match_text:
            return RouteDecision("und", "Undetermined", 0.0, {}, {})
        token_set = set(tokens)
        if not token_set:
            return RouteDecision("und", "Undetermined", 0.0, {}, {})
        ngrams = set(character_ngrams(match_text))
        scores: Dict[str, float] = {}
        signals: Dict[str, List[str]] = {}

        for profile in self.profiles:
            score = 0.0
            found: List[str] = []

            stop_hits = sorted(token_set & self._stopword_index[profile.code])
            keyword_hits = sorted(token_set & self._keyword_index[profile.code])
            char_hits = sorted(char for char in profile.unique_chars if char in normalised)

            if stop_hits:
                score += len(stop_hits) * 1.0
                found.extend(f"stop:{hit}" for hit in stop_hits[:5])
            if keyword_hits:
                score += len(keyword_hits) * 2.0
                found.extend(f"keyword:{hit}" for hit in keyword_hits[:5])
            if char_hits:
                score += len(char_hits) * 1.5
                found.extend(f"char:{hit}" for hit in char_hits[:5])

            profile_ngrams = set()
            for item in profile.stopwords + profile.keywords:
                profile_ngrams.update(character_ngrams(item))
            overlap = ngrams & profile_ngrams
            if overlap:
                score += min(len(overlap) * 0.08, 2.5)

            scores[profile.code] = round(score, 4)
            signals[profile.code] = found

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        best_code, best_score = ranked[0] if ranked else ("und", 0.0)
        total_positive = sum(value for value in scores.values() if value > 0)
        confidence = best_score / total_positive if total_positive else 0.0

        if best_score <= 0:
            return RouteDecision("und", "Undetermined", 0.0, scores, signals)

        profile = self.profile_by_code[best_code]
        return RouteDecision(
            language_code=profile.code,
            language_name=profile.name,
            confidence=round(float(confidence), 4),
            scores=scores,
            signals=signals,
        )

    def route_many(self, texts: Iterable[str]) -> List[RouteDecision]:
        """Route multiple texts."""

        return [self.route(text) for text in texts]

    def route_selectively(
        self,
        text: str,
        *,
        min_confidence: float = 0.0,
        min_score_margin: float = 0.0,
    ) -> SelectiveRouteDecision:
        """Route text and abstain when the evidence does not meet both thresholds."""

        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1.")
        if not math.isfinite(min_score_margin) or min_score_margin < 0.0:
            raise ValueError("min_score_margin must be finite and non-negative.")

        decision = self.route(text)
        margin = score_margin(decision.scores)
        low_confidence = decision.confidence < min_confidence
        narrow_margin = margin < min_score_margin

        if decision.language_code == "und":
            reason = "undetermined"
        elif low_confidence and narrow_margin:
            reason = "low_confidence_and_narrow_score_margin"
        elif low_confidence:
            reason = "low_confidence"
        elif narrow_margin:
            reason = "narrow_score_margin"
        else:
            return SelectiveRouteDecision(
                decision=decision,
                accepted=True,
                accepted_language_code=decision.language_code,
                accepted_language_name=decision.language_name,
                score_margin=margin,
                abstention_reason=None,
            )

        return SelectiveRouteDecision(
            decision=decision,
            accepted=False,
            accepted_language_code=None,
            accepted_language_name=None,
            score_margin=margin,
            abstention_reason=reason,
        )

    def route_many_selectively(
        self,
        texts: Iterable[str],
        *,
        min_confidence: float = 0.0,
        min_score_margin: float = 0.0,
    ) -> List[SelectiveRouteDecision]:
        """Apply one selective routing policy to several texts."""

        return [
            self.route_selectively(
                text,
                min_confidence=min_confidence,
                min_score_margin=min_score_margin,
            )
            for text in texts
        ]


def softmax_scores(scores: Mapping[str, float]) -> Dict[str, float]:
    """Convert arbitrary scores into a probability-like distribution."""

    if not scores:
        return {}
    max_score = max(scores.values())
    exps = {label: math.exp(score - max_score) for label, score in scores.items()}
    total = sum(exps.values()) or 1.0
    return {label: value / total for label, value in exps.items()}
