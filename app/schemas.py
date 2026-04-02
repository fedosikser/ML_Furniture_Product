from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


PageType = Literal["product_page", "listing_page", "non_product_page", "unknown"]
StatusType = Literal["ok", "error"]


class ExtractRequest(BaseModel):
    url: HttpUrl


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
    html: str
