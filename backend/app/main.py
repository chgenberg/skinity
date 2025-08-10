from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from .config import get_settings
from .database import create_db_and_tables, get_session
from .routers import providers, products, search, health
from .scrapers.example import ExampleScraper
from .scrapers.generic_jsonld import GenericJSONLDScraper
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