from __future__ import annotations

import time
from collections import defaultdict

import httpx

from app.classifiers import classify_page
from app.cleaners import clean_candidates
from app.parser import PageFetcher, parse_html
from app.schemas import ExtractResponse, ParsedPage
from app.utils import is_valid_http_url


SOURCE_WEIGHTS = {
    "json_ld": 100,
    "h1": 80,
    "og_title": 70,
    "title": 60,
    "product_cards": 40,
    "breadcrumbs": 20,
    "body": 10,
}


class ProductExtractor:
    def __init__(self, fetcher: PageFetcher | None = None) -> None:
        self.fetcher = fetcher or PageFetcher()

    async def extract(self, url: str) -> ExtractResponse:
        started_at = time.perf_counter()
        if not is_valid_http_url(url):
            return ExtractResponse(
                url=url,
                status="error",
                page_type="unknown",
                message="Invalid URL. Use http or https.",
            )

        try:
            fetched = await self.fetcher.fetch(url)
        except httpx.TimeoutException:
            return ExtractResponse(
                url=url,
                status="error",
                page_type="unknown",
                message="Request timed out while fetching the page.",
            )
        except httpx.HTTPStatusError as exc:
            return ExtractResponse(
                url=url,
                status="error",
                page_type="unknown",
                message=f"Could not fetch page: HTTP {exc.response.status_code}.",
            )
        except (httpx.HTTPError, ValueError) as exc:
            return ExtractResponse(
                url=url,
                status="error",
                page_type="unknown",
                message=str(exc) or "Could not fetch page.",
            )

        response = self.extract_from_html(fetched.url, fetched.final_url, fetched.html)
        response.processing_ms = int((time.perf_counter() - started_at) * 1000)
        return response

    def extract_from_html(self, url: str, final_url: str, html: str) -> ExtractResponse:
        parsed = parse_html(url, final_url, html)
        page_type = classify_page(parsed)
        products, sources = rank_candidates(parsed)
        top_product = products[0] if products else None

        return ExtractResponse(
            url=final_url,
            status="ok",
            page_type=page_type,
            products=products,
            top_product=top_product,
            sources=sources,
            message=None if products else "No product names were found on the page.",
        )


def rank_candidates(page: ParsedPage) -> tuple[list[str], list[str]]:
    scores: dict[str, int] = defaultdict(int)
    candidate_sources: dict[str, set[str]] = defaultdict(set)
    original_names: dict[str, str] = {}

    groups = {
        "json_ld": page.json_ld_products,
        "h1": page.h1,
        "og_title": [page.og_title] if page.og_title else [],
        "title": [page.title] if page.title else [],
        "product_cards": page.product_cards,
        "breadcrumbs": page.breadcrumbs,
        "body": page.body_candidates,
    }

    for source, values in groups.items():
        for value in clean_candidates(values):
            key = value.casefold()
            original_names[key] = value
            scores[key] += SOURCE_WEIGHTS[source]
            candidate_sources[key].add(source)

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            -item[1],
            len(original_names[item[0]]),
            original_names[item[0]].casefold(),
        ),
    )
    products = [original_names[key] for key, _ in ranked[:12]]
    used_sources = sorted({source for key, _ in ranked[:12] for source in candidate_sources[key]})
    return products, used_sources
