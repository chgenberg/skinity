from __future__ import annotations
from typing import Iterable, List, Optional
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import get_settings


class ScrapedProduct:
    def __init__(
        self,
        provider_name: str,
        name: str,
        url: str | None,
        price_amount: float | None,
        price_currency: str | None = "SEK",
        inci: Optional[list[str]] = None,
    ):
        self.provider_name = provider_name
        self.name = name
        self.url = url
        self.price_amount = price_amount
        self.price_currency = price_currency or "SEK"
        self.inci = inci


class BaseScraper:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = httpx.Client(
            headers={"User-Agent": self.settings.scraper_user_agent},
            timeout=20,
            follow_redirects=True,
        )

    def close(self) -> None:
        self.client.close()

    @retry(wait=wait_exponential(multiplier=0.5, min=1, max=8), stop=stop_after_attempt(3))
    def fetch_html(self, url: str) -> str:
        resp = self.client.get(url)
        resp.raise_for_status()
        return resp.text

    def parse(self, html: str) -> List[ScrapedProduct]:
        raise NotImplementedError

    def run(self) -> List[ScrapedProduct]:
        raise NotImplementedError 