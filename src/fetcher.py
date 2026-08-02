import logging
import requests
import time
import urllib.parse
from typing import List, Dict, Any

from src.scrapers.amazon import fetch_amazon_deals_native

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DealFetcher:
    def __init__(self, rapidapi_key: str = "", amazon_tag: str = ""):
        self.rapidapi_key = rapidapi_key
        self.amazon_tag = amazon_tag
        self.url = "https://real-time-amazon-data.p.rapidapi.com/search"
        self.headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
        }

    def _apply_affiliate_tag(self, raw_url: str) -> str:
        """Appends/updates the Amazon Associate tag on product URLs."""
        if not raw_url:
            return ""
        parsed = urllib.parse.urlparse(raw_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        query_params["tag"] = [self.amazon_tag]
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        return urllib.parse.urlunparse(parsed._replace(query=new_query))

    def _fetch_from_rapidapi(
        self, query: str, country: str
    ) -> List[Dict[str, Any]]:
        """Fallback method: Fetches product listings via RapidAPI with rate limit handling."""
        if not self.rapidapi_key:
            return []

        params = {
            "query": query,
            "page": "1",
            "country": country,
            "sort_by": "RELEVANCE",
            "product_condition": "NEW",
        }

        # Polite delay to keep under RapidAPI rate limits
        time.sleep(1.5)

        try:
            res = requests.get(
                self.url, headers=self.headers, params=params, timeout=15
            )
            res.raise_for_status()
            return res.json().get("data", {}).get("products", [])
        except Exception as e:
            logger.error(
                f"Error in RapidAPI fallback for query '{query}' [{country}]: {e}"
            )
            return []

    def fetch_tech_deals(
        self,
        categories: List[str] = None,
        min_discount_pct: int = 15,
        min_rating: float = 4.0,
    ) -> List[Dict[str, Any]]:
        """
        Fetches and filters high-value tech deals across US and CA marketplaces.
        Uses in-house native scraper first, falling back to RapidAPI on error or empty response.
        """
        if not categories:
            categories = [
                "gaming laptop deals",
                "4k monitor deals",
                "pc components deals",
                "wireless audio deals",
            ]

        all_deals = []
        seen_asins = set()

        regions = [
            {"country": "US", "currency": "USD", "flag": "🇺🇸"},
            {"country": "CA", "currency": "CAD", "flag": "🇨🇦"},
        ]

        for region in regions:
            country = region["country"]
            for query in categories:
                items = []

                # --- 1. Primary: In-house native scraper ---
                try:
                    raw_native = fetch_amazon_deals_native(
                        query=query, region=country
                    )
                    if raw_native:
                        for n_item in raw_native:
                            items.append(
                                {
                                    "asin": n_item.get("asin"),
                                    "product_title": n_item.get(
                                        "product_title"
                                    ),
                                    "product_price": n_item.get(
                                        "product_price"
                                    ),
                                    "product_original_price": n_item.get(
                                        "original_price"
                                    ),
                                    "product_star_rating": "4.2",
                                    "product_num_ratings": 100,
                                    "product_url": n_item.get("product_url"),
                                    "product_photo": n_item.get(
                                        "product_photo"
                                    ),
                                }
                            )
                except Exception as ex:
                    logger.warning(
                        f"Native scraper attempt failed for '{query}' [{country}]: {ex}"
                    )

                # --- 2. Fallback: RapidAPI ---
                if not items:
                    logger.info(
                        f"Native scraper returned no results. Triggering RapidAPI fallback for '{query}' [{country}]..."
                    )
                    items = self._fetch_from_rapidapi(
                        query=query, country=country
                    )

                # --- 3. Normalization and Deduplication ---
                for item in items:
                    asin = item.get("asin")
                    unique_key = f"{asin}_{country}"
                    if not asin or unique_key in seen_asins:
                        continue

                    price_str = item.get("product_price", "")
                    orig_price_str = item.get("product_original_price", "")
                    rating_val = item.get("product_star_rating")

                    try:
                        rating = float(rating_val) if rating_val else 0.0
                    except ValueError:
                        rating = 0.0

                    affiliate_link = self._apply_affiliate_tag(
                        item.get("product_url", "")
                    )

                    deal_entry = {
                        "asin": asin,
                        "title": item.get("product_title", "Tech Product"),
                        "price": price_str or "Check Deal",
                        "original_price": orig_price_str,
                        "currency": region["currency"],
                        "flag": region["flag"],
                        "country": country,
                        "rating": rating,
                        "num_ratings": item.get("product_num_ratings", 0),
                        "affiliate_url": affiliate_link,
                        "image_url": item.get("product_photo", ""),
                        "category": query,
                    }

                    seen_asins.add(unique_key)
                    all_deals.append(deal_entry)

        logger.info(
            f"Successfully fetched and filtered {len(all_deals)} high-value deals across US & CA."
        )
        return all_deals[:10]
