from __future__ import annotations
from typing import List, Set
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup

from .base import BaseScraper


STOP_SLUGS: Set[str] = {
    "sv", "varumarken", "varumärken", "nyheter", "erbjudanden", "kampanj", "kundservice",
    "club", "om-lyko", "jobb", "salonger", "rabattkoder", "topplista", "cookies", "privacy",
}


class LykoCatalogScraper(BaseScraper):
    def __init__(self, base_url: str = "https://lyko.com") -> None:
        super().__init__()
        # Base is the domain; we will handle /sv paths explicitly
        self.base_url = base_url.rstrip("/")

    def _abs(self, href: str) -> str:
        return urljoin(self.base_url + "/", href)

    def _is_internal(self, href: str) -> bool:
        netloc = urlparse(self._abs(href)).netloc
        return netloc.endswith("lyko.com")

    def _extract_slug(self, path: str) -> str | None:
        # Normalize and try to pull a brand slug from supported patterns
        # Supported examples: /sv/varumarken/aco, /sv/aco, /varumarken/aco
        parts = [p for p in path.split("/") if p]
        if not parts:
            return None
        # Allow optional locale prefix
        if parts[0] in {"sv", "en", "no", "fi", "da"}:
            parts = parts[1:]
            if not parts:
                return None
        if parts[0] in {"varumarken", "varumärken"} and len(parts) >= 2:
            slug = parts[1]
        else:
            slug = parts[0]
        if not slug or slug in STOP_SLUGS or len(slug) < 2:
            return None
        # Accept unicode letters, digits, dashes and percent-encoding
        if not re.fullmatch(r"[A-Za-z0-9\-%åäöÅÄÖ]+", slug):
            return None
        return slug

    def list_brand_roots(self) -> List[str]:
        """Return absolute brand root URLs sorted A-Z from /sv/varumarken page."""
        # Try both with and without locale prefix
        urls_to_try = ["/sv/varumarken", "/varumarken"]
        slugs: set[str] = set()
        for path in urls_to_try:
            try:
                html = self.fetch_html(self._abs(path))
            except Exception:
                continue
            soup = BeautifulSoup(html, "lxml")
            for a in soup.find_all("a", href=True):
                href = a.get("href") or ""
                if not href or href.startswith("#"):
                    continue
                if not self._is_internal(href):
                    continue
                abs_url = self._abs(href)
                parsed = urlparse(abs_url)
                slug = self._extract_slug(parsed.path.rstrip("/"))
                if not slug:
                    continue
                slugs.add(slug.lower())
        # Build canonical URLs as /sv/<slug>
        return [urljoin(self.base_url + "/", f"/sv/{s}") for s in sorted(slugs)]

    def list_brand_products(self, brand_root: str, limit: int = 100) -> List[str]:
        """Return product-like URLs found under a brand root page (best-effort)."""
        try:
            html = self.fetch_html(brand_root)
        except Exception:
            return []
        soup = BeautifulSoup(html, "lxml")
        product_urls: list[str] = []
        seen: set[str] = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href") or ""
            if not href or href.startswith("#"):
                continue
            if not self._is_internal(href):
                continue
            abs_url = self._abs(href)
            parsed = urlparse(abs_url)
            path = parsed.path
            # Heuristics: exclude brand and utility paths, look for deeper product-like paths
            if any(seg in path for seg in ("/varumarken", "/varumärken")):
                continue
            # Product path guesses commonly have multiple segments and often include a hyphenated slug
            depth = len([p for p in path.split("/") if p])
            looks_like_product = depth >= 3 or re.search(r"[0-9]", path)
            if not looks_like_product:
                continue
            if abs_url in seen:
                continue
            seen.add(abs_url)
            product_urls.append(abs_url)
            if len(product_urls) >= limit:
                break
        return product_urls 