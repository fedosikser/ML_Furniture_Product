from __future__ import annotations

from app.schemas import PageType, ParsedPage


def classify_page(page: ParsedPage) -> PageType:
    product_signals = 0
    listing_signals = 0

    if page.json_ld_products:
        product_signals += 3
    if page.add_to_cart_detected:
        product_signals += 2
    if page.sku_detected:
        product_signals += 1
    if page.price_count > 0:
        product_signals += 1
    if len(page.h1) == 1:
        product_signals += 1

    if len(page.product_cards) >= 3:
        listing_signals += 3
    if len(page.product_cards) >= 6:
        listing_signals += 2
    if page.price_count >= 3:
        listing_signals += 1
    if len(page.h1) > 1:
        listing_signals += 1

    if product_signals >= 4 and product_signals >= listing_signals:
        return "product_page"
    if listing_signals >= 3:
        return "listing_page"
    if product_signals == 0 and listing_signals == 0:
        return "non_product_page"
    if product_signals > listing_signals:
        return "product_page"
    if listing_signals > product_signals:
        return "listing_page"
    return "unknown"

