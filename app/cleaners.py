from __future__ import annotations

import html
import re
from collections import OrderedDict


STOP_WORDS = {
    "home",
    "shop",
    "catalog",
    "collection",
    "collections",
    "sale",
    "products",
    "product",
    "furniture",
    "store",
    "gift card",
}

NOISE_PATTERNS = (
    re.compile(r"^\W+$"),
    re.compile(r"^[\d\s]+$"),
    re.compile(r"(privacy policy|terms|contact us|about us)", re.I),
)


def normalize_text(value: str) -> str:
    text = html.unescape(value or "")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[\t\r\n]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.strip(" -|>:/")
    return text.strip()


def canonical_key(value: str) -> str:
    text = normalize_text(value).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def looks_like_product_name(value: str) -> bool:
    text = normalize_text(value)
    key = canonical_key(text)
    if len(text) < 4 or len(text) > 140:
        return False
    if key in STOP_WORDS:
        return False
    if len(key.split()) == 1 and key in STOP_WORDS:
        return False
    if sum(char.isalpha() for char in text) < 3:
        return False
    if sum(char in "!@#$%^&*_=+[]{}" for char in text) > 4:
        return False
    return not any(pattern.search(text) for pattern in NOISE_PATTERNS)


def unique_preserve_order(values: list[str]) -> list[str]:
    ordered: OrderedDict[str, str] = OrderedDict()
    for value in values:
        normalized = normalize_text(value)
        if not normalized:
            continue
        key = canonical_key(normalized)
        if key and key not in ordered:
            ordered[key] = normalized
    return list(ordered.values())


def clean_candidates(values: list[str]) -> list[str]:
    return unique_preserve_order(
        [value for value in values if looks_like_product_name(value)]
    )

