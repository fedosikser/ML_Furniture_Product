from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


PageType = Literal["product_page", "listing_page", "non_product_page", "unknown"]
StatusType = Literal["ok", "error"]


class ExtractRequest(BaseModel):
    url: HttpUrl


class ProductCandidate(BaseModel):
    name: str
    score: int = Field(ge=0)
    sources: list[str] = Field(default_factory=list)


class ExtractResponse(BaseModel):
    url: str
    status: StatusType
    page_type: PageType
    products: list[str] = Field(default_factory=list)
    top_product: str | None = None
    sources: list[str] = Field(default_factory=list)
    message: str | None = None
    processing_ms: int | None = None


class ParsedPage(BaseModel):
    url: str
    final_url: str
    title: str | None = None
    h1: list[str] = Field(default_factory=list)
    og_title: str | None = None
    json_ld_products: list[str] = Field(default_factory=list)
    product_cards: list[str] = Field(default_factory=list)
    breadcrumbs: list[str] = Field(default_factory=list)
    body_candidates: list[str] = Field(default_factory=list)
    price_count: int = 0
    add_to_cart_detected: bool = False
    sku_detected: bool = False


class FetchResult(BaseModel):
    url: str
    final_url: str
    status_code: int
    html: str


class UrlBatch(BaseModel):
    urls: list[str]

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]

