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
    query: str, region: str = "US", max_retries: int = 3
) -> List[Dict]:
    """
    Scrapes Amazon search directly for deal listings.
    
    Returns structured dict objects with keys matching RapidAPI spec:
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

                # URL Link
                link_elem = item.find("a", class_="a-link-normal s-no-hover") or item.find(
                    "a", class_="a-link-normal"
                )
                href = link_elem.get("href", "") if link_elem else ""
                product_url = (
                    f"{base_url}{href}"
                    if href.startswith("/")
                    else f"{base_url}/dp/{asin}"
                )

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
                    deals.append(
                        {
                            "asin": asin,
                            "product_title": title,
                            "product_price": f"${current_price:.2f}",
                            "raw_price": current_price,
                            "original_price": (
                                f"${original_price:.2f}"
                                if original_price
                                else None
                            ),
                            "raw_original_price": original_price,
                            "discount_percentage": discount_pct,
                            "product_url": product_url,
                            "product_photo": photo_url,
                            "currency": currency,
                            "region": region,
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
