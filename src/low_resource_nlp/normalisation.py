"""Text normalisation helpers for low-resource NLP experiments."""

from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass
from typing import List

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
USER_RE = re.compile(r"(?<!\w)@\w+")
HASHTAG_RE = re.compile(r"(?<!\w)#([\w_]+)")
MULTISPACE_RE = re.compile(r"\s+")
REPEATED_CHAR_RE = re.compile(r"(.)\1{2,}", re.IGNORECASE)
JOINER_CHARS = {"-", "'"}


@dataclass(frozen=True)
class NormalisationConfig:
    """Configuration for text normalisation.

    Diacritics are preserved by default because they carry meaning in languages
    such as Yoruba. Use `strip_diacritics=True` only for matching/indexing.
    """

    lowercase: bool = True
    normalise_unicode: str = "NFC"
    preserve_diacritics: bool = True
    replace_urls: bool = True
    replace_users: bool = True
    unpack_hashtags: bool = True
    reduce_repeated_chars: bool = True
    repeated_char_limit: int = 2


def strip_diacritics(text: str) -> str:
    """Remove combining marks while keeping base characters."""

    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def split_hashtag(match: re.Match[str]) -> str:
    """Convert `#LowResourceNLP` into readable text."""

    raw = match.group(1).replace("_", " ")
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", raw)
    return spaced


def normalise_text(text: str, config: NormalisationConfig | None = None) -> str:
    """Normalise text while preserving linguistically meaningful characters."""

    cfg = config or NormalisationConfig()
    value = html.unescape(text or "")
    value = unicodedata.normalize(cfg.normalise_unicode, value)

    if cfg.replace_urls:
        value = URL_RE.sub(" <URL> ", value)
    if cfg.replace_users:
        value = USER_RE.sub(" <USER> ", value)
    if cfg.unpack_hashtags:
        value = HASHTAG_RE.sub(split_hashtag, value)
    if cfg.reduce_repeated_chars:
        limit = max(1, cfg.repeated_char_limit)
        value = REPEATED_CHAR_RE.sub(lambda match: match.group(1) * limit, value)
    if not cfg.preserve_diacritics:
        value = strip_diacritics(value)
    if cfg.lowercase:
        value = value.lower()

    return MULTISPACE_RE.sub(" ", value).strip()


def normalise_for_matching(text: str) -> str:
    """Return a lower-cased, accent-insensitive representation for matching."""

    return normalise_text(
        text,
        NormalisationConfig(
            lowercase=True,
            preserve_diacritics=False,
            replace_urls=True,
            replace_users=True,
            unpack_hashtags=True,
        ),
    )


def tokenise_words(text: str, *, match_form: bool = False) -> List[str]:
    """Tokenise a text into Unicode-aware word tokens."""

    value = normalise_for_matching(text) if match_form else normalise_text(text)
    tokens: List[str] = []
    current: List[str] = []

    for index, char in enumerate(value):
        category = unicodedata.category(char)
        is_word_char = category.startswith("L") or category.startswith("M")
        is_joiner = (
            char in JOINER_CHARS
            and current
            and index + 1 < len(value)
            and unicodedata.category(value[index + 1]).startswith("L")
        )

        if is_word_char or is_joiner:
            current.append(char)
            continue

        if current:
            tokens.append("".join(current).strip("-'"))
            current = []

    if current:
        tokens.append("".join(current).strip("-'"))

    return [token for token in tokens if token]
