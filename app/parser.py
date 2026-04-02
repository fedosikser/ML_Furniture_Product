from __future__ import annotations

import json
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.cleaners import clean_candidates, normalize_text
from app.schemas import FetchResult, ParsedPage
from app.utils import build_user_agent


PRODUCT_CARD_SELECTORS = (
    "[data-product-title]",
    "[class*='product'] [class*='title']",
    "[class*='product'] [class*='name']",
    "[class*='card'] [class*='title']",
    "a[href*='/products/']",
)

PRICE_PATTERN = re.compile(r"[$€£]\s?\d")
SKU_PATTERN = re.compile(r"\bsku\b", re.I)
ADD_TO_CART_PATTERN = re.compile(r"add to cart|buy now", re.I)


class PageFetcher:
    async def fetch(self, url: str) -> FetchResult:
        headers = {"User-Agent": build_user_agent()}
        timeout = httpx.Timeout(12.0, connect=6.0)
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "html" not in content_type:
                raise ValueError("URL did not return HTML content")
            return FetchResult(
                url=url,
                final_url=str(response.url),
                status_code=response.status_code,
                html=response.text,
            )


def _collect_json_ld_names(payload: Any) -> list[str]:
    names: list[str] = []
    if isinstance(payload, list):
        for item in payload:
            names.extend(_collect_json_ld_names(item))
        return names
    if isinstance(payload, dict):
        item_type = payload.get("@type")
        if item_type == "Product" and isinstance(payload.get("name"), str):
            names.append(payload["name"])
        graph = payload.get("@graph")
        if graph:
            names.extend(_collect_json_ld_names(graph))
    return names


def parse_html(url: str, final_url: str, html: str) -> ParsedPage:
    soup = BeautifulSoup(html, "lxml")

    title = normalize_text(soup.title.get_text(" ", strip=True)) if soup.title else None
    og_title_node = soup.find("meta", attrs={"property": "og:title"})
    og_title = normalize_text(og_title_node.get("content", "")) if og_title_node else None

    h1 = clean_candidates([node.get_text(" ", strip=True) for node in soup.find_all("h1")])
    breadcrumbs = clean_candidates(
        [
            node.get_text(" ", strip=True)
            for node in soup.select("[aria-label*='breadcrumb' i] a, nav.breadcrumb a, .breadcrumb a")
        ]
    )

    json_ld_products: list[str] = []
    for node in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = node.string or node.get_text(" ", strip=True)
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        json_ld_products.extend(_collect_json_ld_names(payload))
    json_ld_products = clean_candidates(json_ld_products)

    product_cards: list[str] = []
    for selector in PRODUCT_CARD_SELECTORS:
        for node in soup.select(selector):
            text = node.get("data-product-title") or node.get_text(" ", strip=True)
            if text:
                product_cards.append(text)
    product_cards = clean_candidates(product_cards)

    body_candidates = clean_candidates(
        [
            text
            for text in soup.stripped_strings
            if 12 <= len(text) <= 90 and "/" not in text and "{" not in text
        ][:80]
    )

    raw_text = soup.get_text(" ", strip=True)

    return ParsedPage(
        url=url,
        final_url=final_url,
        title=title,
        h1=h1,
        og_title=og_title,
        json_ld_products=json_ld_products,
        product_cards=product_cards,
        breadcrumbs=breadcrumbs,
        body_candidates=body_candidates,
        price_count=len(PRICE_PATTERN.findall(raw_text)),
        add_to_cart_detected=bool(ADD_TO_CART_PATTERN.search(raw_text)),
        sku_detected=bool(SKU_PATTERN.search(raw_text)),
    )

