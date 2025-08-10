from __future__ import annotations
from typing import Iterable, List, Tuple
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup

from .base import BaseScraper


CATEGORY_STOP_SLUGS = {
    # generic categories
    "makeup", "smink", "hudvard", "hudvård", "harvard", "hårvård", "parfym", "doft",
    "presenttips", "presentkort", "kampanj", "nyheter", "varumarken", "varumärken",
    "sminkverktyg", "ansiktsvard", "ansiktsvård", "kroppsvard", "kroppsvård",
    # site/about/misc
    "om-kicks", "press", "jobb", "jobba-hos-kicks", "integritetspolicy", "cookies",
    "kundservice", "samarbeta-med-oss", "vinnare", "klubb", "club", "kicks-club",
    "hallbarhet", "h\u00e5llbarhet", "tavlingsvillkor", "t\u00e4vlingsvillkor",
}


class KicksCatalogScraper(BaseScraper):
    def __init__(self, base_url: str = "https://www.kicks.se") -> None:
        super().__init__()
        self.base_url = base_url.rstrip("/")

    def _absolute(self, href: str) -> str:
        return urljoin(self.base_url + "/", href)

    def _is_internal(self, href: str) -> bool:
        netloc = urlparse(self._absolute(href)).netloc
        return netloc.endswith("kicks.se")

    def list_brand_roots(self) -> List[str]:
        """Return absolute URLs for brand root pages like /aco, /abercrombie-fitch, sorted A-Z."""
        html = self.fetch_html(self._absolute("/varumarken"))
        soup = BeautifulSoup(html, "lxml")
        slugs: set[str] = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href") or ""
            if not href or href.startswith("#"):
                continue
            if not self._is_internal(href):
                continue
            path = urlparse(self._absolute(href)).path.rstrip("/")
            segs = [s for s in path.split("/") if s]
            if len(segs) != 1:
                continue
            slug = segs[0]
            if slug in CATEGORY_STOP_SLUGS:
                continue
            if not re.fullmatch(r"[a-z0-9-]{2,}", slug):
                continue
            slugs.add(slug)
        return [self._absolute(f"/{s}") for s in sorted(slugs)]

    def _looks_like_brand(self, slug: str) -> bool:
        """Fetch the candidate brand page and ensure it contains product links under /{slug}/..."""
        try:
            html = self.fetch_html(self._absolute(f"/{slug}"))
        except Exception:
            return False
        soup = BeautifulSoup(html, "lxml")
        for a in soup.find_all("a", href=True):
            path = urlparse(self._absolute(a.get("href") or "")).path.rstrip("/")
            segs = [s for s in path.split("/") if s]
            if len(segs) >= 2 and segs[0] == slug:
                return True
        return False

    def list_brands(self, max_brands: int | None = None) -> List[Tuple[str, str]]:
        """Return list of (brand_slug, brand_url) discovered on /varumarken.
        Filters out known category slugs and keeps only single-segment paths, then verifies page contains products.
        """
        html = self.fetch_html(self._absolute("/varumarken"))
        soup = BeautifulSoup(html, "lxml")
        seen: set[str] = set()
        verified: List[Tuple[str, str]] = []
        candidates: List[Tuple[str, str]] = []
        for a in soup.find_all("a", href=True):
            href = a.get("href") or ""
            text = (a.get_text(strip=True) or "").lower()
            if not href or href.startswith("#"):
                continue
            if not self._is_internal(href):
                continue
            path = urlparse(self._absolute(href)).path.rstrip("/")
            if not path or path in {"/", "/varumarken"}:
                continue
            segments = [s for s in path.split("/") if s]
            if len(segments) != 1:
                continue
            slug = segments[0]
            if slug in CATEGORY_STOP_SLUGS or (text and text in CATEGORY_STOP_SLUGS):
                continue
            if not re.fullmatch(r"[a-z0-9-]{2,}", slug):
                continue
            if slug in seen:
                continue
            seen.add(slug)
            candidates.append((slug, self._absolute(path)))
            if self._looks_like_brand(slug):
                verified.append((slug, self._absolute(path)))
                if max_brands and len(verified) >= max_brands:
                    return verified
        # Fallback: if verification yields nothing, return top candidates (up to max_brands)
        if not verified:
            return candidates[: (max_brands or len(candidates))]
        return verified

    def list_brand_products(self, brand_slug: str, max_pages: int = 5) -> List[str]:
        """Return product URLs for a given brand by crawling brand listing pages."""
        collected: set[str] = set()
        page = 1
        while page <= max_pages:
            url = self._absolute(f"/{brand_slug}?page={page}") if page > 1 else self._absolute(f"/{brand_slug}")
            try:
                html = self.fetch_html(url)
            except Exception:
                break
            soup = BeautifulSoup(html, "lxml")
            for a in soup.find_all("a", href=True):
                href = a.get("href") or ""
                if not href or not self._is_internal(href):
                    continue
                path = urlparse(self._absolute(href)).path.rstrip("/")
                segs = [s for s in path.split("/") if s]
                if len(segs) >= 2 and segs[0] == brand_slug:
                    if any(x in path for x in ["/filter", "/filtrera", "/bilder", "/image"]):
                        continue
                    collected.add(self._absolute(path))
            page += 1
        return sorted(collected)

    def list_all_products(self, max_brands: int | None = None, max_pages_per_brand: int = 3) -> List[Tuple[str, str]]:
        """Return list of (brand_slug, product_url) across brands."""
        pairs: List[Tuple[str, str]] = []
        for slug, _ in self.list_brands(max_brands=max_brands):
            try:
                urls = self.list_brand_products(slug, max_pages=max_pages_per_brand)
            except Exception:
                continue
            for u in urls:
                pairs.append((slug, u))
        return pairs 