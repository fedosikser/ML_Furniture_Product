from app.classifiers import classify_page
from app.schemas import ParsedPage


def test_classify_product_page() -> None:
    page = ParsedPage(
      url="https://example.com/product",
      final_url="https://example.com/product",
      h1=["Modern Oak Dining Table"],
      json_ld_products=["Modern Oak Dining Table"],
      price_count=1,
      add_to_cart_detected=True,
    )
    assert classify_page(page) == "product_page"


def test_classify_listing_page() -> None:
    page = ParsedPage(
      url="https://example.com/collection",
      final_url="https://example.com/collection",
      product_cards=["Chair One", "Chair Two", "Chair Three", "Chair Four"],
      price_count=4,
    )
    assert classify_page(page) == "listing_page"
