from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.extractor import ProductExtractor
from app.schemas import ExtractRequest, ExtractResponse


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(title="Furniture Product Extractor", version="0.1.0")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
extractor = ProductExtractor()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/style.css")
async def stylesheet() -> FileResponse:
    return FileResponse(TEMPLATES_DIR / "style.css", media_type="text/css")


@app.get("/script.js")
async def script() -> FileResponse:
    return FileResponse(TEMPLATES_DIR / "script.js", media_type="application/javascript")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
async def extract_products(payload: ExtractRequest) -> ExtractResponse:
    return await extractor.extract(str(payload.url))
