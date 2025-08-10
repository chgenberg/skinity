from __future__ import annotations
from typing import List, Optional
from urllib.parse import urlparse
import re
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapedProduct


PRODUCT_KEYWORDS = re.compile(r"product|/p/|/prod/|/artiklar/|/produkt/|/sku/|/item/|/shop/", re.IGNORECASE)


class GenericJSONLDScraper(BaseScraper):
    def __init__(self, domain: str, max_pages: int = 50) -> None:
        super().__init__()
        self.domain = domain
        self.max_pages = max_pages

    def _robots_sitemaps(self) -> List[str]:
        candidates = [f"https://{self.domain}/robots.txt", f"https://www.{self.domain}/robots.txt"]
        urls: List[str] = []
        for r in candidates:
            try:
                txt = self.fetch_html(r)
                for line in txt.splitlines():
                    if line.lower().startswith("sitemap:"):
                        u = line.split(":", 1)[1].strip()
                        if u and u not in urls:
                            urls.append(u)
            except Exception:
                continue
        return urls

    def _sitemap_urls(self) -> List[str]:
        roots = [
            f"https://{self.domain}/sitemap.xml",
            f"https://www.{self.domain}/sitemap.xml",
            f"http://{self.domain}/sitemap.xml",
        ] + self._robots_sitemaps()
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
        props = pdata.get("additionalProperty")
        items: list[str] = []
        if isinstance(props, list):
            for p in props:
                if isinstance(p, dict) and str(p.get("name", "")).lower() in {"inci", "ingredients"}:
                    val = p.get("value")
                    if isinstance(val, str):
                        items.extend([s.strip() for s in re.split(r",|;|\n", val) if s.strip()])
        val = pdata.get("ingredients")
        if isinstance(val, str):
            items.extend([s.strip() for s in re.split(r",|;|\n", val) if s.strip()])
        has_ing = pdata.get("hasIngredient")
        if isinstance(has_ing, list):
            for v in has_ing:
                if isinstance(v, dict) and "name" in v:
                    items.append(str(v["name"]).strip())
                elif isinstance(v, str):
                    items.append(v.strip())
        return list(dict.fromkeys(items)) if items else None

    def _extract_jsonld_product(self, html: str) -> Optional[dict]:
        # 1) Fast scan
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
            pass
        # 2) Robust parse via BeautifulSoup
        try:
            soup = BeautifulSoup(html, "lxml")
            for script in soup.find_all("script", {"type": "application/ld+json"}):
                try:
                    data = json.loads(script.string or "{}")
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

    def _extract_html_fallback(self, html: str) -> Optional[dict]:
        try:
            soup = BeautifulSoup(html, "lxml")
            # Name
            name = None
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                name = og_title["content"].strip()
            if not name and soup.title:
                name = soup.title.text.strip()

            # Price & currency from common meta/itemprop
            price = None
            currency = None
            mp = soup.find("meta", property="product:price:amount") or soup.find("meta", itemprop="price")
            if mp and mp.get("content"):
                price = mp["content"].strip()
            mc = soup.find("meta", property="product:price:currency") or soup.find("meta", itemprop="priceCurrency")
            if mc and mc.get("content"):
                currency = mc["content"].strip()

            # Ingredients by heading labels
            inci: list[str] = []
            heading = soup.find(string=re.compile(r"Ingredienser|Ingredients", re.IGNORECASE))
            if heading:
                # try parent block
                block = heading.parent
                if block:
                    text = block.get_text(" ", strip=True)
                    # extract after label
                    parts = re.split(r"Ingredienser|Ingredients", text, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        raw = parts[1]
                        inci = [s.strip() for s in re.split(r",|;|\n", raw) if s.strip()]
            if not any([name, price, inci]):
                return None
            return {
                "name": name,
                "offers": {"price": price, "priceCurrency": currency} if price else {},
                "ingredients": ", ".join(inci) if inci else None,
            }
        except Exception:
            return None

    def run(self) -> List[ScrapedProduct]:
        urls = self._sitemap_urls()
        results: List[ScrapedProduct] = []
        for url in urls[: self.max_pages]:
            try:
                html = self.fetch_html(url)
                pdata = self._extract_jsonld_product(html)
                if not pdata:
                    pdata = self._extract_html_fallback(html)
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
                inci = self._extract_inci(pdata) if pdata else None
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