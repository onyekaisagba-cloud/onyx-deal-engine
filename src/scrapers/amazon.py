"""
Onyx Deal Engine - In-House Amazon Scraping Module
File: src/scrapers/amazon.py
"""

import logging
import random
import re
import time
from typing import Dict, List, Optional
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Standard user-agent rotators for modern browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
]

DOMAINS = {
    "US": "https://www.amazon.com",
    "CA": "https://www.amazon.ca",
}

CURRENCIES = {
    "US": "USD",
    "CA": "CAD",
}

# Expanded Multi-Industry Target Search Queries (Covers all 20+ pSEO Categories)
TARGET_SEARCH_QUERIES = [
    # 1. Evergreen Digital & SaaS / Security
    "software subscription deals",
    "antivirus security software deals",
    "cloud storage subscription deals",

    # 2. High-Frequency Fashion & Accessories
    "men women sneakers apparel sale",
    "designer watches sale",
    "backpacks travel bags sale",

    # 3. Travel & Hospitality Gear
    "travel carry on luggage deals",
    "travel neck pillow packing cubes deals",

    # 4. Health, Fitness & Wellness
    "workout gym gear deals",
    "protein whey supplement deals",
    "fitness smartwatch deals",

    # 5. Core Tech & Hardware
    "gaming laptop deals",
    "4k oled monitor deals",
    "graphics card rtx deals",
    "ps5 accessories deals",
    "noise canceling headphones deals",
    "handheld gaming pc deals",
    "gaming mouse keyboard deals",
    "nvme ssd deals",
    "smart home alexa deals",

    # 6. Intent & Budget Terms
    "best tech deals under 50",
    "best tech deals under 100"
]


def _get_headers(region: str) -> Dict[str, str]:
    """Generates sanitized browser headers mimicking direct web user requests."""
    tld = "com" if region == "US" else "ca"
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": f"https://www.amazon.{tld}/",
        "Device-Memory": "8",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    }


def parse_price(price_str: str) -> Optional[float]:
    """Extracts numeric price float from currency strings (e.g. '$299.99' -> 299.99)."""
    if not price_str:
        return None
    cleaned = re.sub(r"[^\d.]", "", price_str.replace(",", ""))
    try:
        return float(cleaned)
    except ValueError:
        return None


def fetch_amazon_deals_native(
    query: str, region: str = "US", max_retries: int = 3, amazon_tag: str = "onyxdeals06-20"
) -> List[Dict]:
    """
    Scrapes Amazon search directly for deal listings.
    
    Returns structured dict objects with keys matching pipeline spec:
    asin, product_title, product_price, original_price, discount_percentage, 
    product_url, product_photo, currency, region
    """
    base_url = DOMAINS.get(region, "https://www.amazon.com")
    search_url = f"{base_url}/s"
    params = {"k": query, "s": "relevance-blender"}
    currency = CURRENCIES.get(region, "USD")

    deals = []

    for attempt in range(1, max_retries + 1):
        try:
            # Exponential backoff delay between requests
            time.sleep(random.uniform(1.2, 2.5))

            with httpx.Client(
                timeout=12.0, follow_redirects=True, http2=True
            ) as client:
                response = client.get(
                    search_url, params=params, headers=_get_headers(region)
                )

            if response.status_code != 200:
                logger.warning(
                    f"Native scraper received HTTP {response.status_code} for '{query}' [{region}]"
                )
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all(
                "div", {"data-component-type": "s-search-result"}
            )

            if not items:
                logger.debug(
                    f"No product containers found on attempt {attempt} for '{query}' [{region}]"
                )
                continue

            for item in items:
                asin = item.get("data-asin")
                if not asin:
                    continue

                # Product Title
                title_elem = item.find("h2")
                title = (
                    title_elem.get_text(strip=True)
                    if title_elem
                    else "Unknown Product"
                )

                # URL Link & Tag Injection
                product_url = f"{base_url}/dp/{asin}?tag={amazon_tag}"

                # Image
                img_elem = item.find("img", class_="s-image")
                photo_url = img_elem.get("src", "") if img_elem else ""

                # Current Price Parsing
                price_whole = item.find("span", class_="a-price-whole")
                price_fraction = item.find("span", class_="a-price-fraction")
                current_price = None

                if price_whole:
                    p_str = (
                        f"{price_whole.get_text(strip=True)}{price_fraction.get_text(strip=True) if price_fraction else '00'}"
                    )
                    current_price = parse_price(p_str)

                # List Price / Original Price Parsing
                orig_price_elem = item.find(
                    "span", class_="a-price a-text-price"
                )
                original_price = None
                if orig_price_elem:
                    offscreen_span = orig_price_elem.find(
                        "span", class_="a-offscreen"
                    )
                    if offscreen_span:
                        original_price = parse_price(
                            offscreen_span.get_text(strip=True)
                        )

                # Calculate discount
                discount_pct = 0.0
                if (
                    current_price
                    and original_price
                    and original_price > current_price
                ):
                    discount_pct = round(
                        ((original_price - current_price) / original_price)
                        * 100,
                        2,
                    )

                if current_price:
                    flag = "🇨🇦" if region == "CA" else "🇺🇸"
                    deals.append(
                        {
                            "asin": asin,
                            "title": title,
                            "product_title": title,
                            "price": f"${current_price:.2f}",
                            "product_price": f"${current_price:.2f}",
                            "raw_price": current_price,
                            "original_price": (
                                f"${original_price:.2f}"
                                if original_price
                                else None
                            ),
                            "raw_original_price": original_price,
                            "discount_percentage": discount_pct,
                            "affiliate_url": product_url,
                            "product_url": product_url,
                            "image_url": photo_url,
                            "product_photo": photo_url,
                            "currency": currency,
                            "region": region,
                            "flag": flag,
                        }
                    )

            if deals:
                logger.info(
                    f"Successfully scraped {len(deals)} items natively for query '{query}' [{region}]"
                )
                return deals

        except Exception as e:
            logger.error(
                f"Error in native scraper (attempt {attempt}) for '{query}' [{region}]: {e}"
            )

    return deals


def fetch_amazon_deals(region: str = "US", amazon_tag: str = "onyxdeals06-20") -> List[Dict]:
    """
    High-level orchestrator function that sweeps through all TARGET_SEARCH_QUERIES.
    Directly imported and executed by src.main.
    """
    all_deals = []
    seen_asins = set()

    for query in TARGET_SEARCH_QUERIES:
        query_deals = fetch_amazon_deals_native(
            query=query, region=region, amazon_tag=amazon_tag
        )
        for deal in query_deals:
            asin = deal.get("asin")
            if asin and asin not in seen_asins:
                seen_asins.add(asin)
                all_deals.append(deal)

    logger.info(f"Total unique multi-category Amazon deals aggregated: {len(all_deals)}")
    return all_deals


class NativeAmazonScraper:
    """Class wrapper providing an object-oriented interface for deal fetching."""

    def __init__(self, amazon_tag: str = "onyxdeals06-20"):
        self.amazon_tag = amazon_tag

    def scrape_query(self, query: str, domain: str = "com") -> List[Dict]:
        region = "CA" if domain.lower() in ["ca", "canada"] else "US"
        return fetch_amazon_deals_native(
            query=query, region=region, amazon_tag=self.amazon_tag
        )

    def scrape_all_categories(self, region: str = "US") -> List[Dict]:
        return fetch_amazon_deals(region=region, amazon_tag=self.amazon_tag)
