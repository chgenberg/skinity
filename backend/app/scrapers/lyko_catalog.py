from __future__ import annotations
from typing import List
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup

from .base import BaseScraper


class LykoCatalogScraper(BaseScraper):
    def __init__(self, base_url: str = "https://lyko.com/sv") -> None:
        super().__init__()
        self.base_url = base_url.rstrip("/")

    def _abs(self, href: str) -> str:
        return urljoin(self.base_url + "/", href)

    def _is_internal(self, href: str) -> bool:
        netloc = urlparse(self._abs(href)).netloc
        return netloc.endswith("lyko.com")

    def list_brand_roots(self) -> List[str]:
        """Return absolute brand root URLs sorted A-Z from /varumarken."""
        html = self.fetch_html(self._abs("/varumarken"))
        soup = BeautifulSoup(html, "lxml")
        slugs: set[str] = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href") or ""
            if not href or href.startswith("#"):
                continue
            if not self._is_internal(href):
                continue
            path = urlparse(self._abs(href)).path.rstrip("/")
            # Accept either /sv/<brand> or /sv/varumarken/<brand>
            if re.fullmatch(r"/sv/[a-z0-9-]+", path):
                slug = path.split("/")[-1]
            elif re.fullmatch(r"/sv/varumarken/[a-z0-9-]+", path):
                slug = path.split("/")[-1]
            else:
                continue
            # Skip the index page and overly short slugs
            if slug in {"varumarken"} or len(slug) < 2:
                continue
            slugs.add(slug)
        return [self._abs(f"/{s}") for s in sorted(slugs)] 