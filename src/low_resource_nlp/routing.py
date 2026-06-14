"""Lightweight language and dialect routing for low-resource NLP."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .normalisation import normalise_for_matching, normalise_text, tokenise_words


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


def default_profiles() -> List[LanguageProfile]:
    """Return default African-language-focused routing profiles."""

    return [
        LanguageProfile(
            code="yor",
            name="Yoruba",
            stopwords=("ati", "ni", "si", "mo", "o", "awon", "fun", "ti", "bi", "ko"),
            keywords=("ekaabo", "bawo", "jowo", "oruko", "ile", "omo", "e", "se"),
            unique_chars=("ẹ", "ọ", "ṣ", "à", "á", "è", "é", "ì", "í", "ò", "ó", "ù", "ú"),
        ),
        LanguageProfile(
            code="ibo",
            name="Igbo",
            stopwords=("na", "nke", "ndi", "ka", "bu", "m", "gi", "anyi", "ha", "o"),
            keywords=("kedu", "biko", "nnoo", "umu", "nne", "nna", "ezi", "okwu"),
            unique_chars=("ị", "ọ", "ụ", "ṅ"),
        ),
        LanguageProfile(
            code="hau",
            name="Hausa",
            stopwords=("da", "na", "ne", "ce", "a", "ya", "ta", "mu", "su", "mai"),
            keywords=("sannu", "ina", "lafiya", "gida", "mutum", "yau", "kuma", "wannan"),
            unique_chars=("ɓ", "ɗ", "ƙ"),
        ),
        LanguageProfile(
            code="pcm",
            name="Nigerian Pidgin",
            stopwords=("dey", "na", "no", "go", "we", "una", "dem", "me", "i", "you"),
            keywords=("abeg", "wahala", "wetin", "sha", "sabi", "pikin", "chop", "oga", "make"),
        ),
        LanguageProfile(
            code="swa",
            name="Swahili",
            stopwords=("na", "ya", "kwa", "ni", "wa", "katika", "hii", "hiyo", "mimi", "wewe"),
            keywords=("habari", "asante", "tafadhali", "sana", "mtu", "watu", "nyumba", "leo"),
        ),
        LanguageProfile(
            code="eng",
            name="English",
            stopwords=("the", "and", "is", "in", "to", "of", "for", "with", "this", "that"),
            keywords=("hello", "please", "model", "language", "research", "data", "music", "emotion"),
        ),
    ]


def character_ngrams(text: str, n: int = 3) -> List[str]:
    """Create character n-grams for compact lexical matching."""

    collapsed = normalise_for_matching(text).replace(" ", "_")
    if len(collapsed) < n:
        return [collapsed] if collapsed else []
    return [collapsed[index : index + n] for index in range(len(collapsed) - n + 1)]


class LexicalLanguageRouter:
    """Dependency-light router using script, lexical, and character signals."""

    def __init__(self, profiles: Sequence[LanguageProfile]):
        self.profiles = list(profiles)
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
        """Build the default router."""

        return cls(default_profiles())

    def route(self, text: str) -> RouteDecision:
        """Route a text to the most likely language profile."""

        normalised = normalise_text(text)
        match_text = normalise_for_matching(text)
        tokens = tokenise_words(text, match_form=True)
        if not match_text:
            return RouteDecision("und", "Undetermined", 0.0, {}, {})
        token_set = set(tokens)
        ngrams = set(character_ngrams(text))
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

            if profile.code == "eng" and match_text.isascii():
                score += 0.2

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


def softmax_scores(scores: Mapping[str, float]) -> Dict[str, float]:
    """Convert arbitrary scores into a probability-like distribution."""

    if not scores:
        return {}
    max_score = max(scores.values())
    exps = {label: math.exp(score - max_score) for label, score in scores.items()}
    total = sum(exps.values()) or 1.0
    return {label: value / total for label, value in exps.items()}
