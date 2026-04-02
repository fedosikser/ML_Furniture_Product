# Furniture Product Extractor

Practical PoC for extracting product names from furniture store pages. The solution uses a hybrid strategy: parse strong HTML signals first, then rank cleaned candidates instead of training a full NER model from scratch.

## Why this approach

- Faster to implement and explain for an internship test task
- More stable on real e-commerce pages with limited labeled data
- Easy to extend later with Playwright or NLP post-processing

## Architecture

- `app/main.py` exposes the FastAPI app and routes
- `app/parser.py` fetches pages and extracts structured HTML signals
- `app/classifiers.py` labels the page as `product_page`, `listing_page`, or `non_product_page`
- `app/cleaners.py` normalizes strings, removes duplicates, and filters noise
- `app/extractor.py` combines all sources, ranks candidates, and returns the final API response
- `templates/index.html`, `templates/style.css`, and `templates/script.js` provide the UI

## Extraction pipeline

1. Validate the input URL.
2. Fetch HTML with `httpx`.
3. Parse `title`, `h1`, `og:title`, `JSON-LD Product.name`, breadcrumbs, and likely product-card titles.
4. Clean and deduplicate candidate names.
5. Classify the page using lightweight heuristics.
6. Rank candidates using source priority:
   - `json_ld`
   - `h1`
   - `og_title`
   - `title`
   - `product_cards`
   - `breadcrumbs`
   - `body`

## API

- `GET /` renders the UI
- `POST /extract` accepts:

```json
{
  "url": "https://example.com/page"
}
```

- `GET /health` returns service status

Example response:

```json
{
  "url": "https://example.com/page",
  "status": "ok",
  "page_type": "product_page",
  "products": [
    "Modern Oak Dining Table",
    "Scandinavian Chair"
  ],
  "top_product": "Modern Oak Dining Table",
  "sources": ["h1", "json_ld", "title"],
  "processing_ms": 184
}
```

## Running locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Then open `http://127.0.0.1:8001`.

If you want a different port:

```bash
PORT=8010 python run.py
```

## Deploy on Render with GitHub

This project is ready for a Render web service deployment.

Files used for deploy:

- `.python-version` sets the Python version for Render
- `render.yaml` describes the web service settings

Start command used on Render:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 1. Push the project to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

### 2. Create the service on Render

1. Open Render Dashboard.
2. Click `New +`.
3. Choose `Blueprint` if you want Render to read `render.yaml`, or choose `Web Service` and connect the repo manually.
4. Connect your GitHub account and select the repository.
5. Confirm these settings:

- Runtime: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Instance Type: `Free`

### 3. After deploy

- Render will give you a public `onrender.com` URL
- open `/health` to check the backend
- open `/` to use the UI

### Notes about the free plan

- Free web services can spin down after inactivity
- the first request after idle can take about a minute
- free hosting is good for a test task or demo, not production

## Testing

```bash
pytest
```

## Limitations

- JS-heavy storefronts may require a Playwright fallback
- Heuristics can pick category labels or branded page titles on unusual sites
- Listing pages vary a lot across stores, so extraction quality is best-effort
- This project is aimed at a clear PoC, not large-scale production crawling
