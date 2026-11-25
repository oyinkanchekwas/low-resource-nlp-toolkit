"""Examine code-switching in multilingual text."""

from __future__ import annotations

import html
import math
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence

from .normalisation import JOINER_CHARS, URL_RE, USER_RE, normalise_text
from .routing import LexicalLanguageRouter, score_margin

AMBIGUOUS = "ambiguous"
UNDETERMINED = "und"
_CHARACTER_REFERENCE = re.compile(r"&(?:#[0-9]+;?|#[xX][0-9a-fA-F]+;?|[^\t\n\f <&#;]{1,32};?)")


@dataclass(frozen=True)
class TokenAudit:
    """Routing evidence for one token.

    Confidence is the winning route's share of the total positive routing score.
    """

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
    """A contiguous run of tokens with the same accepted route.

    Mean confidence averages the tokens' relative routing scores.
    """

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
    """Word-level language results for a short multilingual text."""

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

    def to_aggregate_dict(self) -> Dict[str, object]:
        """Return token counts, language count, and code-switch ratio.

        Aggregate values can still reveal information about small inputs.
        """
        return {
            "token_count": self.token_count,
            "routed_token_count": self.routed_token_count,
            "accepted_token_count": self.accepted_token_count,
            "language_count": len(self.language_mix),
            "code_switch_ratio": self.code_switch_ratio,
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


def _ignored_text_ranges(text: str) -> List[tuple[int, int]]:
    """Locate links and usernames in the original text after HTML decoding."""
    decoded: List[str] = []
    offsets: List[tuple[int, int]] = []
    nonword_references: List[tuple[int, int]] = []
    position = 0

    def append_literal(value: str, start: int) -> None:
        decoded.extend(value)
        offsets.extend((start + i, start + i + 1) for i in range(len(value)))

    # Decoded characters retain their source interval so character offsets stay in
    # the original input even when an HTML reference changes length.
    for match in _CHARACTER_REFERENCE.finditer(text):
        append_literal(text[position : match.start()], position)
        original = match.group()
        replacement = html.unescape(original)
        if replacement == original:
            append_literal(original, match.start())
        else:
            decoded.extend(replacement)
            offsets.extend([(match.start(), match.end())] * len(replacement))
            if not any(unicodedata.category(char)[0] in {"L", "M"} for char in replacement):
                nonword_references.append(match.span())
        position = match.end()
    append_literal(text[position:], position)
    value = "".join(decoded)
    matches = [(match.start(), match.end()) for match in URL_RE.finditer(value)]
    for match in USER_RE.finditer(value):
        start, end = match.span()
        if start and unicodedata.category(value[start - 1]).startswith("M"):
            cluster_start = start - 1
            while cluster_start and unicodedata.category(value[cluster_start]).startswith("M"):
                cluster_start -= 1
            preceding = unicodedata.normalize("NFC", value[cluster_start:start])
            if preceding and re.match(r"\w", preceding[-1]):
                continue
        while end < len(value) and (
            re.match(r"\w", value[end]) or unicodedata.category(value[end]).startswith("M")
        ):
            end += 1
        matches.append((start, end))
    ranges = sorted(
        nonword_references + [(offsets[start][0], offsets[end - 1][1]) for start, end in matches]
    )
    merged: List[tuple[int, int]] = []
    for start, end in ranges:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _language_name(router: LexicalLanguageRouter, code: str) -> str:
    if code == AMBIGUOUS:
        return "Ambiguous"
    if code == UNDETERMINED:
        return "Undetermined"
    profile = router.profile_by_code.get(code)
    return profile.name if profile else code


def _validate_thresholds(min_confidence: float, min_score_margin: float) -> None:
    if not 0.0 <= min_confidence <= 1.0:
        raise ValueError("min_confidence must be between 0 and 1.")
    if not math.isfinite(min_score_margin) or min_score_margin < 0.0:
        raise ValueError("min_score_margin must be finite and non-negative.")


def audit_token(
    token: str,
    start: int,
    end: int,
    *,
    router: LexicalLanguageRouter,
    min_confidence: float,
    min_score_margin: float,
) -> TokenAudit:
    """Suggest a language for a word using the configured thresholds."""

    _validate_thresholds(min_confidence, min_score_margin)
    decision = router.route(token)
    margin = score_margin(decision.scores)
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


def _build_spans(
    text: str, tokens: Sequence[TokenAudit], ignored_ranges: Sequence[tuple[int, int]] = ()
) -> List[LanguageSpan]:
    spans: List[LanguageSpan] = []
    if not tokens:
        return spans

    current_code = tokens[0].accepted_language_code
    current_name = tokens[0].accepted_language_name
    current_tokens: List[TokenAudit] = []
    range_index = 0

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
        if current_tokens:
            while (
                range_index < len(ignored_ranges)
                and ignored_ranges[range_index][1] <= current_tokens[-1].end
            ):
                range_index += 1
        separated = (
            current_tokens
            and range_index < len(ignored_ranges)
            and ignored_ranges[range_index][0] < token.start
            and ignored_ranges[range_index][1] > current_tokens[-1].end
        )
        if token.accepted_language_code != current_code or separated:
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
    """Examine word-level language changes within a short text.

    Use the results for corpus analysis, never identity inference. It favours
    abstention when token-level evidence is weak or confusable.
    Confidence values express the winning route's share of positive routing scores.
    Links, usernames, and non-word HTML character references are excluded from
    token evidence; the original text is retained in the report.
    """

    _validate_thresholds(min_confidence, min_score_margin)
    if router is None:
        raise ValueError("Supply a router configured with caller-supplied language profiles.")
    active_router = router
    ignored_ranges = _ignored_text_ranges(text or "")
    masked = list(text or "")
    for begin, end in ignored_ranges:
        masked[begin:end] = " " * (end - begin)
    token_offsets = [
        (text[start:end], start, end) for _, start, end in iter_word_offsets("".join(masked))
    ]
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
    if not tokens and ignored_ranges:
        warnings = ["no_auditable_tokens"]

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
        spans=tuple(_build_spans(text, tokens, ignored_ranges)),
    )
