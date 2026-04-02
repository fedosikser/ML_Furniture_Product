from __future__ import annotations

from urllib.parse import urlparse


def build_user_agent() -> str:
    return (
        "Mozilla/5.0 (compatible; FurnitureExtractorBot/1.0; "
        "+https://example.local/extractor)"
    )


def is_valid_http_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

