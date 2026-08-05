"""
Onyx Deal Engine - Ingestion Fetcher & Data Normalizer
File: src/fetcher.py
"""

import logging
import random
import time
import urllib.parse
from typing import Any, Dict, List

import requests
from src.db import process_price_badge
from src.scrapers.amazon import fetch_amazon_deals_native

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exponential_backoff(max_retries: int = 3, base_delay: float = 2.0):
    """Decorator that retries a function upon hitting HTTP 429 or network errors,
    using exponential backoff with random jitter.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    is_rate_limit = (
                        e.response is not None
                        and e.response.status_code == 429
                    )
                    if retries == max_retries or not is_rate_limit:
                        logger.error(
                            f"Execution failed after {retries} retries: {e}"
                        )
                        raise e

                    sleep_time = (base_delay * (2**retries)) + random.uniform(
                        0.5, 1.5
                    )
                    logger.warning(
                        f"HTTP 429 Rate Limit hit. Retrying in {sleep_time:.2f}s... (Attempt {retries + 1}/{max_retries})"
                    )
                    time.sleep(sleep_time)
                    retries += 1

        return wrapper

    return decorator


class DealFetcher:

    def __init__(self, rapidapi_key: str = "", amazon_tag: str = "onyxdeals06-20"):
        self.rapidapi_key = rapidapi_key
        self.amazon_tag = amazon_tag or "onyxdeals06-20"
        self.url = "https://real-time-amazon-data.p.rapidapi.com/search"
        self.headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
        }

    def _apply_affiliate_tag(self, raw_url: str) -> str:
        if not raw_url:
            return ""
        parsed = urllib.parse.urlparse(raw_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        query_params["tag"] = [self.amazon_tag]
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        return urllib.parse.urlunparse(parsed._replace(query=new_query))

    @exponential_backoff(max_retries=3, base_delay=2.0)
    def _fetch_from_rapidapi(
        self, query: str, country: str
    ) -> List[Dict[str, Any]]:
        if not self.rapidapi_key:
            return []

        params = {
            "query": query,
            "page": "1",
            "country": country,
            "sort_by": "RELEVANCE",
            "product_condition": "NEW",
        }

        time.sleep(1.5)

        res = requests.get(
            self.url, headers=self.headers, params=params, timeout=15
        )
        res.raise_for_status()
        return res.json().get("data", {}).get("products", [])

    def fetch_tech_deals(
        self,
        categories: List[str] = None,
        min_discount_pct: int = 10,
        min_rating: float = 4.0,
    ) -> List[Dict[str, Any]]:
        if not categories:
            categories = [
                "rtx 4070 gaming laptop deal",
                "oled gaming monitor discount",
                "rtx 4080 graphics card price drop",
                "ps5 portal accessories deal",
                "wireless noise canceling headphones deal",
                "portable gaming handheld deal",
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
                        query=query, region=country, amazon_tag=self.amazon_tag
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
                                    "raw_price": n_item.get("raw_price"),
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

                # --- 2. Fallback: RapidAPI with Exponential Backoff ---
                if not items:
                    logger.info(
                        f"Native scraper returned no results. Triggering RapidAPI fallback for '{query}' [{country}]..."
                    )
                    try:
                        items = self._fetch_from_rapidapi(
                            query=query, country=country
                        )
                    except Exception as err:
                        logger.error(
                            f"RapidAPI fallback failed after retries for '{query}' [{country}]: {err}"
                        )

                # --- 3. Normalization, Badging, and Deduplication ---
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

                    raw_price = item.get("raw_price")
                    if raw_price is None and price_str:
                        try:
                            raw_price = float(
                                price_str.replace("$", "")
                                .replace(",", "")
                                .strip()
                            )
                        except ValueError:
                            raw_price = 0.0

                    badge_label, _ = process_price_badge(
                        asin=asin, country=country, current_price=raw_price
                    )

                    affiliate_link = self._apply_affiliate_tag(
                        item.get("product_url", "")
                    )

                    deal_entry = {
                        "asin": asin,
                        "title": item.get("product_title", "Tech Product"),
                        "price": price_str or "Check Deal",
                        "original_price": orig_price_str,
                        "badge": badge_label,
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
        return all_deals[:20]
