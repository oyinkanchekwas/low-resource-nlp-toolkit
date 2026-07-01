"""Evidence-first audits for noisy and code-switched low-resource text."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence

from .normalisation import JOINER_CHARS, normalise_text
from .routing import LexicalLanguageRouter

AMBIGUOUS = "ambiguous"
UNDETERMINED = "und"


@dataclass(frozen=True)
class TokenAudit:
    """Routing evidence for one token."""

    text: str
    normalised: str
    start: int
    end: int
    language_code: str
    language_name: str
    accepted_language_code: str
    accepted_language_name: str
    confidence: float
    score_margin: float
    scores: Mapping[str, float]
    signals: Mapping[str, List[str]]

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-serialisable representation."""

        return {
            "text": self.text,
            "normalised": self.normalised,
            "start": self.start,
            "end": self.end,
            "language_code": self.language_code,
            "language_name": self.language_name,
            "accepted_language_code": self.accepted_language_code,
            "accepted_language_name": self.accepted_language_name,
            "confidence": self.confidence,
            "score_margin": self.score_margin,
            "scores": dict(self.scores),
            "signals": {key: list(value) for key, value in self.signals.items()},
        }


@dataclass(frozen=True)
class LanguageSpan:
    """A contiguous run of tokens with the same accepted route."""

    language_code: str
    language_name: str
    start: int
    end: int
    text: str
    token_count: int
    mean_confidence: float

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-serialisable representation."""

        return {
            "language_code": self.language_code,
            "language_name": self.language_name,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "token_count": self.token_count,
            "mean_confidence": self.mean_confidence,
        }


@dataclass(frozen=True)
class CodeSwitchAudit:
    """Structured audit for a short multilingual text."""

    text: str
    dominant_language_code: str
    dominant_language_name: str
    token_count: int
    routed_token_count: int
    accepted_token_count: int
    language_mix: Mapping[str, int]
    code_switch_ratio: float
    warnings: Sequence[str] = field(default_factory=tuple)
    tokens: Sequence[TokenAudit] = field(default_factory=tuple)
    spans: Sequence[LanguageSpan] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-serialisable representation."""

        return {
            "text": self.text,
            "dominant_language_code": self.dominant_language_code,
            "dominant_language_name": self.dominant_language_name,
            "token_count": self.token_count,
            "routed_token_count": self.routed_token_count,
            "accepted_token_count": self.accepted_token_count,
            "language_mix": dict(self.language_mix),
            "code_switch_ratio": self.code_switch_ratio,
            "warnings": list(self.warnings),
            "tokens": [token.to_dict() for token in self.tokens],
            "spans": [span.to_dict() for span in self.spans],
        }


def iter_word_offsets(text: str) -> List[tuple[str, int, int]]:
    """Return Unicode-aware word tokens with offsets in the original text."""

    tokens: List[tuple[str, int, int]] = []
    current: List[str] = []
    start: int | None = None

    def flush() -> None:
        nonlocal current, start
        if not current or start is None:
            return
        raw = "".join(current)
        value = raw.strip("-'")
        if value:
            left_trim = len(raw) - len(raw.lstrip("-'"))
            right_trim = len(raw.rstrip("-'"))
            tokens.append((value, start + left_trim, start + right_trim))
        current = []
        start = None

    for index, char in enumerate(text or ""):
        category = unicodedata.category(char)
        is_word_char = category.startswith("L") or category.startswith("M")
        is_joiner = (
            char in JOINER_CHARS
            and current
            and index + 1 < len(text)
            and unicodedata.category(text[index + 1]).startswith("L")
        )

        if is_word_char or is_joiner:
            if start is None:
                start = index
            current.append(char)
            continue

        flush()

    flush()

    return tokens


def _score_margin(scores: Mapping[str, float]) -> float:
    positive = sorted((score for score in scores.values() if score > 0), reverse=True)
    if not positive:
        return 0.0
    if len(positive) == 1:
        return round(positive[0], 4)
    return round(positive[0] - positive[1], 4)


def _language_name(router: LexicalLanguageRouter, code: str) -> str:
    if code == AMBIGUOUS:
        return "Ambiguous"
    if code == UNDETERMINED:
        return "Undetermined"
    profile = router.profile_by_code.get(code)
    return profile.name if profile else code


def audit_token(
    token: str,
    start: int,
    end: int,
    *,
    router: LexicalLanguageRouter,
    min_confidence: float,
    min_score_margin: float,
) -> TokenAudit:
    """Audit one token and decide whether its route is strong enough to use."""

    decision = router.route(token)
    margin = _score_margin(decision.scores)
    normalised = normalise_text(token)

    if decision.language_code == UNDETERMINED:
        accepted_code = UNDETERMINED
    elif decision.confidence < min_confidence or margin < min_score_margin:
        accepted_code = AMBIGUOUS
    else:
        accepted_code = decision.language_code

    return TokenAudit(
        text=token,
        normalised=normalised,
        start=start,
        end=end,
        language_code=decision.language_code,
        language_name=decision.language_name,
        accepted_language_code=accepted_code,
        accepted_language_name=_language_name(router, accepted_code),
        confidence=decision.confidence,
        score_margin=margin,
        scores=decision.scores,
        signals=decision.signals,
    )


def _build_spans(text: str, tokens: Sequence[TokenAudit]) -> List[LanguageSpan]:
    spans: List[LanguageSpan] = []
    if not tokens:
        return spans

    current_code = tokens[0].accepted_language_code
    current_name = tokens[0].accepted_language_name
    current_tokens: List[TokenAudit] = []

    def flush() -> None:
        if not current_tokens:
            return
        start = current_tokens[0].start
        end = current_tokens[-1].end
        mean_confidence = sum(token.confidence for token in current_tokens) / len(current_tokens)
        spans.append(
            LanguageSpan(
                language_code=current_code,
                language_name=current_name,
                start=start,
                end=end,
                text=text[start:end],
                token_count=len(current_tokens),
                mean_confidence=round(mean_confidence, 4),
            )
        )

    for token in tokens:
        if token.accepted_language_code != current_code:
            flush()
            current_code = token.accepted_language_code
            current_name = token.accepted_language_name
            current_tokens = [token]
        else:
            current_tokens.append(token)

    flush()
    return spans


def _dominant_language(
    router: LexicalLanguageRouter,
    language_mix: Mapping[str, int],
) -> tuple[str, str]:
    if not language_mix:
        return UNDETERMINED, "Undetermined"
    code = sorted(language_mix.items(), key=lambda item: (-item[1], item[0]))[0][0]
    return code, _language_name(router, code)


def _warnings(
    *,
    token_count: int,
    routed_token_count: int,
    accepted_token_count: int,
    language_mix: Mapping[str, int],
    code_switch_ratio: float,
) -> List[str]:
    warnings: List[str] = []
    if token_count == 0:
        return ["empty_text"]
    if accepted_token_count == 0:
        warnings.append("no_supported_language_evidence")
    if routed_token_count > accepted_token_count:
        warnings.append("ambiguous_or_weak_token_routes")
    if accepted_token_count and accepted_token_count / token_count < 0.5:
        warnings.append("low_supported_language_coverage")
    if len(language_mix) > 1:
        warnings.append("mixed_language_signals")
    if code_switch_ratio >= 0.35:
        warnings.append("high_code_switching")
    return warnings


def audit_code_switching(
    text: str,
    *,
    router: LexicalLanguageRouter | None = None,
    min_confidence: float = 0.55,
    min_score_margin: float = 0.75,
) -> CodeSwitchAudit:
    """Audit language evidence across tokens in a short text.

    The audit is designed for corpus triage rather than identity inference. It
    favours abstention when token-level evidence is weak or confusable.
    """

    active_router = router or LexicalLanguageRouter.default()
    token_offsets = iter_word_offsets(text)
    tokens = [
        audit_token(
            token,
            start,
            end,
            router=active_router,
            min_confidence=min_confidence,
            min_score_margin=min_score_margin,
        )
        for token, start, end in token_offsets
    ]

    language_mix: Dict[str, int] = {}
    routed_token_count = 0
    accepted_token_count = 0
    for token in tokens:
        if token.language_code != UNDETERMINED:
            routed_token_count += 1
        if token.accepted_language_code not in {AMBIGUOUS, UNDETERMINED}:
            accepted_token_count += 1
            language_mix[token.accepted_language_code] = (
                language_mix.get(token.accepted_language_code, 0) + 1
            )

    dominant_code, dominant_name = _dominant_language(active_router, language_mix)
    if accepted_token_count and dominant_code != UNDETERMINED:
        non_dominant = accepted_token_count - language_mix.get(dominant_code, 0)
        code_switch_ratio = round(non_dominant / accepted_token_count, 4)
    else:
        code_switch_ratio = 0.0

    warnings = _warnings(
        token_count=len(tokens),
        routed_token_count=routed_token_count,
        accepted_token_count=accepted_token_count,
        language_mix=language_mix,
        code_switch_ratio=code_switch_ratio,
    )

    return CodeSwitchAudit(
        text=text,
        dominant_language_code=dominant_code,
        dominant_language_name=dominant_name,
        token_count=len(tokens),
        routed_token_count=routed_token_count,
        accepted_token_count=accepted_token_count,
        language_mix=dict(sorted(language_mix.items())),
        code_switch_ratio=code_switch_ratio,
        warnings=tuple(warnings),
        tokens=tuple(tokens),
        spans=tuple(_build_spans(text, tokens)),
    )
