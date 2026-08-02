"""
Onyx Deal Engine - Best Buy Native Scraper with CJ Affiliate Wrapping
File: src/scrapers/bestbuy.py
"""

import logging
import os
import urllib.parse
from typing import Any, Dict, List
from bs4 import BeautifulSoup
import httpx

logger = logging.getLogger(__name__)


def wrap_cj_link(destination_url: str) -> str:
    """Wraps a raw product URL into a CJ Affiliate deep link."""
    website_id = os.getenv("CJ_WEBSITE_ID", "").strip()
    if not website_id or not destination_url:
        return destination_url

    encoded_dest = urllib.parse.quote(destination_url, safe="")
    # CJ's standard deep-linking redirect structure
    return f"https://www.anrdoezrs.net/click-{website_id}-1234567?url={encoded_dest}"


def fetch_bestbuy_deals_native(
    query: str = "laptop deals", region: str = "US"
) -> List[Dict[str, Any]]:
    """Scrapes Best Buy search results and applies CJ Affiliate tracking links."""
    domain = (
        "https://www.bestbuy.ca" if region == "CA" else "https://www.bestbuy.com"
    )
    search_url = (
        f"{domain}/site/searchpage.jsp"
        if region == "US"
        else f"{domain}/en-ca/search"
    )

    params = {"st": query} if region == "US" else {"search": query}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    scraped_items = []

    try:
        with httpx.Client(
            timeout=12.0, follow_redirects=True, http2=True
        ) as client:
            res = client.get(search_url, params=params, headers=headers)
            if res.status_code != 200:
                logger.warning(
                    f"Best Buy returned status {res.status_code} for query '{query}' [{region}]"
                )
                return []

            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select(".sku-item, li.productLine_2N92G")

            for card in cards[:8]:
                title_elem = card.select_one(
                    ".sku-title a, div.productItemName_3IZ3c"
                )
                price_elem = card.select_one(
                    ".priceView-customer-price span, div.price_1a932"
                )
                link_elem = card.select_one(
                    "a[href*='/product/'], a[href*='/site/']"
                )
                img_elem = card.select_one("img.product-image, img[src*='bestbuy']")

                if not title_elem or not price_elem:
                    continue

                title = title_elem.get_text(strip=True)
                price_str = price_elem.get_text(strip=True)

                raw_href = (
                    link_elem["href"]
                    if link_elem and link_elem.has_attr("href")
                    else ""
                )
                raw_prod_url = (
                    f"{domain}{raw_href}"
                    if raw_href.startswith("/")
                    else raw_href
                )
                img_url = (
                    img_elem["src"]
                    if img_elem and img_elem.has_attr("src")
                    else ""
                )

                # Wrap raw URL into CJ Affiliate link
                affiliate_url = wrap_cj_link(raw_prod_url)

                try:
                    raw_price = float(
                        price_str.replace("$", "").replace(",", "").strip()
                    )
                except ValueError:
                    raw_price = 0.0

                scraped_items.append(
                    {
                        "asin": f"BB_{hash(title) % 1000000}",
                        "product_title": title,
                        "product_price": price_str,
                        "raw_price": raw_price,
                        "original_price": "",
                        "product_url": raw_prod_url,
                        "affiliate_url": affiliate_url,
                        "product_photo": img_url,
                        "source": "BestBuy",
                    }
                )

        logger.info(
            f"Successfully scraped {len(scraped_items)} Best Buy deals with CJ tracking for '{query}' [{region}]"
        )
        return scraped_items

    except Exception as e:
        logger.error(f"Error scraping Best Buy for '{query}' [{region}]: {e}")
        return []
