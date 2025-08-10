from __future__ import annotations
from typing import List
from .base import BaseScraper, ScrapedProduct


class ExampleScraper(BaseScraper):
    def run(self) -> List[ScrapedProduct]:
        items: List[ScrapedProduct] = [
            ScrapedProduct(
                "ExampleBrand",
                "Hydrating Serum",
                "https://example.com/serum",
                249.0,
                "SEK",
                ["Aqua", "Glycerin", "Sodium Hyaluronate"],
            ),
            ScrapedProduct(
                "ExampleBrand",
                "Gentle Cleanser",
                "https://example.com/cleanser",
                149.0,
                "SEK",
                ["Aqua", "Cocamidopropyl Betaine", "Citric Acid"],
            ),
        ]
        return items 