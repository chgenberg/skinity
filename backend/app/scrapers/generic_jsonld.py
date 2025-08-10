from __future__ import annotations
from typing import List, Optional
from urllib.parse import urlparse
import re
import json
import xml.etree.ElementTree as ET

from .base import BaseScraper, ScrapedProduct


PRODUCT_KEYWORDS = re.compile(r"product|/p/|/prod/|/artiklar/|/produkt/|/artiklar/|/sku/", re.IGNORECASE)


class GenericJSONLDScraper(BaseScraper):
    def __init__(self, domain: str, max_pages: int = 50) -> None:
        super().__init__()
        self.domain = domain
        self.max_pages = max_pages

    def _sitemap_urls(self) -> List[str]:
        roots = [
            f"https://{self.domain}/sitemap.xml",
            f"https://www.{self.domain}/sitemap.xml",
            f"http://{self.domain}/sitemap.xml",
        ]
        seen: set[str] = set()
        found: List[str] = []
        for root in roots:
            try:
                xml = self.fetch_html(root)
                for url in self._parse_sitemap(xml):
                    if url not in seen:
                        seen.add(url)
                        found.append(url)
            except Exception:
                continue
        return found

    def _parse_sitemap(self, xml_text: str) -> List[str]:
        urls: List[str] = []
        try:
            tree = ET.fromstring(xml_text.encode("utf-8"))
        except Exception:
            return urls
        ns = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "image": "http://www.google.com/schemas/sitemap-image/1.1",
        }
        for loc in tree.findall(".//sm:sitemap/sm:loc", ns):
            try:
                xml = self.fetch_html(loc.text or "")
                urls.extend(self._parse_sitemap(xml))
            except Exception:
                continue
        for loc in tree.findall(".//sm:url/sm:loc", ns):
            if not loc.text:
                continue
            url = loc.text.strip()
            if self.domain in urlparse(url).netloc and PRODUCT_KEYWORDS.search(url):
                urls.append(url)
        return urls

    def _extract_inci(self, pdata: dict) -> Optional[list[str]]:
        # Try common places
        # 1) additionalProperty (GS1/Schema.org pattern)
        props = pdata.get("additionalProperty")
        items = []
        if isinstance(props, list):
            for p in props:
                if isinstance(p, dict) and str(p.get("name", "")).lower() in {"inci", "ingredients"}:
                    val = p.get("value")
                    if isinstance(val, str):
                        items.extend([s.strip() for s in re.split(r",|;|\n", val) if s.strip()])
        # 2) ingredients directly
        val = pdata.get("ingredients")
        if isinstance(val, str):
            items.extend([s.strip() for s in re.split(r",|;|\n", val) if s.strip()])
        # 3) hasIngredient list
        has_ing = pdata.get("hasIngredient")
        if isinstance(has_ing, list):
            for v in has_ing:
                if isinstance(v, dict) and "name" in v:
                    items.append(str(v["name"]).strip())
                elif isinstance(v, str):
                    items.append(v.strip())
        return list(dict.fromkeys(items)) if items else None

    def _extract_jsonld_product(self, html: str) -> Optional[dict]:
        try:
            start_tag = '<script type="application/ld+json">'
            pos = 0
            while True:
                idx = html.find(start_tag, pos)
                if idx == -1:
                    break
                end = html.find("</script>", idx)
                if end == -1:
                    break
                chunk = html[idx + len(start_tag): end]
                pos = end + 9
                try:
                    data = json.loads(chunk)
                except Exception:
                    continue
                candidates = data if isinstance(data, list) else [data]
                for c in candidates:
                    t = c.get("@type")
                    if t == "Product" or (isinstance(t, list) and "Product" in t):
                        return c
        except Exception:
            return None
        return None

    def run(self) -> List[ScrapedProduct]:
        urls = self._sitemap_urls()
        results: List[ScrapedProduct] = []
        for url in urls[: self.max_pages]:
            try:
                html = self.fetch_html(url)
                pdata = self._extract_jsonld_product(html)
                if not pdata:
                    continue
                brand_name = None
                brand = pdata.get("brand")
                if isinstance(brand, dict):
                    brand_name = brand.get("name")
                elif isinstance(brand, str):
                    brand_name = brand
                name = pdata.get("name") or pdata.get("sku") or url
                offers = pdata.get("offers")
                price = None
                currency = None
                if isinstance(offers, dict):
                    price = offers.get("price") or offers.get("lowPrice")
                    currency = offers.get("priceCurrency")
                inci = self._extract_inci(pdata)
                scraped = ScrapedProduct(
                    brand_name or self.domain,
                    name,
                    url,
                    float(price) if price else None,
                    currency or "SEK",
                    inci,
                )
                results.append(scraped)
            except Exception:
                continue
        return results 