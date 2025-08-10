from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Iterator
import csv
import io
from sqlmodel import Session
from .config import get_settings
from .database import create_db_and_tables, get_session
from .routers import providers, products, search, health
from .scrapers.example import ExampleScraper
from .scrapers.generic_jsonld import GenericJSONLDScraper
from .scrapers.kicks_catalog import KicksCatalogScraper
from .scrapers.registry import TARGET_DOMAINS
from .models import Provider, Product
from .crud import create_provider, create_product, get_or_create_provider_by_name, get_product_by_url

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(providers.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(search.router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/")
def root():
    return {"status": "ok", "name": settings.app_name}


@app.post("/api/scrape/run")
def run_example_scraper(session: Session = Depends(get_session)):
    scraper = ExampleScraper()
    items = scraper.run()
    provider = get_or_create_provider_by_name(session, "ExampleBrand")

    created = 0
    for it in items:
        if it.url and get_product_by_url(session, it.url):
            continue
        product = Product(
            provider_id=provider.id,
            name=it.name,
            url=it.url,
            price_amount=it.price_amount,
            price_currency=it.price_currency,
            tags=["mock"],
            inci=it.inci,
        )
        create_product(session, product)
        created += 1
    return {"created": created}


@app.post("/api/scrape/run_all")
def run_all_scrapers(limit_per_domain: int = 50, session: Session = Depends(get_session)):
    total_created = 0
    for domain in TARGET_DOMAINS:
        scraper = GenericJSONLDScraper(domain=domain, max_pages=limit_per_domain)
        items = scraper.run()
        for it in items:
            provider = get_or_create_provider_by_name(session, it.provider_name)
            if it.url and get_product_by_url(session, it.url):
                continue
            product = Product(
                provider_id=provider.id,
                name=it.name,
                url=it.url,
                price_amount=it.price_amount,
                price_currency=it.price_currency,
                tags=["scraped", domain],
                inci=it.inci,
            )
            create_product(session, product)
            total_created += 1
    return {"created": total_created, "domains": TARGET_DOMAINS}


@app.post("/api/scrape/run_domain")
def run_single_domain(domain: str, limit: int = 50, session: Session = Depends(get_session)):
    """Scrape a single domain, e.g., kicks.se or kicks.com, with a page limit."""
    scraper = GenericJSONLDScraper(domain=domain, max_pages=limit)
    items = scraper.run()
    created = 0
    for it in items:
        provider = get_or_create_provider_by_name(session, it.provider_name)
        if it.url and get_product_by_url(session, it.url):
            continue
        product = Product(
            provider_id=provider.id,
            name=it.name,
            url=it.url,
            price_amount=it.price_amount,
            price_currency=it.price_currency,
            tags=["scraped", domain],
            inci=it.inci,
        )
        create_product(session, product)
        created += 1
    return {"created": created, "domain": domain}


class URLList(BaseModel):
    urls: List[str]
    domain: str | None = None


@app.post("/api/scrape/run_urls")
def run_urls(payload: URLList, session: Session = Depends(get_session)):
    domain = payload.domain or (payload.urls[0].split("/")[2] if payload.urls else "unknown")
    scraper = GenericJSONLDScraper(domain=domain, max_pages=len(payload.urls))
    created = 0
    for url in payload.urls:
        try:
            item = scraper.scrape_url(url)
        except Exception:
            continue
        if not item:
            continue
        provider = get_or_create_provider_by_name(session, item.provider_name)
        if item.url and get_product_by_url(session, item.url):
            continue
        product = Product(
            provider_id=provider.id,
            name=item.name,
            url=item.url,
            price_amount=item.price_amount,
            price_currency=item.price_currency,
            tags=["scraped", domain],
            inci=item.inci,
        )
        create_product(session, product)
        created += 1
    return {"created": created, "count": len(payload.urls), "domain": domain}


@app.get("/api/kicks/catalog.csv")
def kicks_catalog_csv(max_brands: int | None = 50, max_pages_per_brand: int = 2):
    scraper = KicksCatalogScraper()
    pairs = scraper.list_all_products(max_brands=max_brands, max_pages_per_brand=max_pages_per_brand)

    def generate() -> Iterator[bytes]:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["brand_slug", "product_url"])
        for slug, url in pairs:
            writer.writerow([slug, url])
        yield buffer.getvalue().encode("utf-8")

    return StreamingResponse(generate(), media_type="text/csv",
                              headers={"Content-Disposition": "attachment; filename=kicks_catalog.csv"}) 