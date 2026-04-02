from app.extractor import ProductExtractor


PRODUCT_HTML = """
<html>
  <head>
    <title>Modern Oak Dining Table | Nord Home</title>
    <meta property="og:title" content="Modern Oak Dining Table" />
    <script type="application/ld+json">
      {"@context":"https://schema.org","@type":"Product","name":"Modern Oak Dining Table"}
    </script>
  </head>
  <body>
    <h1>Modern Oak Dining Table</h1>
    <button>Add to cart</button>
    <span>$499</span>
  </body>
</html>
"""


LISTING_HTML = """
<html>
  <head><title>Dining Chairs Collection</title></head>
  <body>
    <div class="product-grid">
      <a href="/products/chair-1">Scandinavian Chair</a>
      <a href="/products/chair-2">Walnut Lounge Chair</a>
      <a href="/products/chair-3">Cane Accent Chair</a>
    </div>
    <span>$120</span>
    <span>$180</span>
    <span>$240</span>
  </body>
</html>
"""


def test_extract_from_product_html() -> None:
    extractor = ProductExtractor()
    result = extractor.extract_from_html("https://example.com/item", "https://example.com/item", PRODUCT_HTML)
    assert result.status == "ok"
    assert result.page_type == "product_page"
    assert result.top_product == "Modern Oak Dining Table"


def test_extract_from_listing_html() -> None:
    extractor = ProductExtractor()
    result = extractor.extract_from_html(
        "https://example.com/collection",
        "https://example.com/collection",
        LISTING_HTML,
    )
    assert result.status == "ok"
    assert result.page_type == "listing_page"
    assert "Scandinavian Chair" in result.products
