"""
Onyx Deal Engine - Dev.to Syndication Publisher
File: src/devto_publisher.py
"""

import logging
import requests
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DevToPublisher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://dev.to/api/articles"
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def _generate_markdown(self, deals: List[Dict[str, Any]]) -> str:
        """Formats the list of deals into a structured Dev.to Markdown article."""
        md = "# 🚀 Daily Tech Deals Vault — Top Picks & Steals\n\n"
        md += "Here are today's top tech deals gathered and verified. *Note: Includes affiliate links.*\n\n---\n\n"

        for i, deal in enumerate(deals, 1):
            title = deal.get("title", "Tech Deal")
            price = deal.get("price", "Check site")
            orig_price = deal.get("original_price")
            rating = deal.get("rating", "N/A")
            num_ratings = deal.get("num_ratings", 0)
            url = deal.get("affiliate_url", "#")
            img = deal.get("image_url", "")

            md += f"### {i}. {title}\n\n"
            if img:
                md += f"![{title}]({img})\n\n"
            
            price_line = f"**Price:** `{price}`"
            if orig_price and orig_price != "None":
                price_line += f" ~~(Was {orig_price})~~"
            md += f"{price_line}\n\n"
            md += f"**Rating:** ⭐ {rating} ({num_ratings} reviews)\n\n"
            md += f"[👉 View Deal on Amazon]({url})\n\n---\n\n"

        md += "\n\n*Updated automatically via Onyx Deal Engine.*"
        return md

    def publish_roundup(self, deals: List[Dict[str, Any]], title: str = None) -> bool:
        """Publishes the deal article to Dev.to with high-CTR keyword titles and rate-limit handling."""
        if not deals:
            logger.warning("No deals available to publish to Dev.to.")
            return False

        if not title:
            # Dynamically extract high-intent buyer keywords from the top scraped deal
            top_deal_title = deals[0].get("title", "Tech") if deals else "Tech"
            short_product = " ".join(top_deal_title.split()[:4])
            now_str = datetime.now().strftime("%B %d, %Y")
            
            # High-CTR Search Title Format
            title = f"🔥 Top Tech Deals: {short_product} & Price Drops ({now_str})"

        markdown_content = self._generate_markdown(deals)
        payload = {
            "article": {
                "title": title,
                "published": True,
                "body_markdown": markdown_content,
                "tags": ["tech", "deals", "hardware", "gadgets"],
                "series": "Onyx Tech Deals"
            }
        }

        try:
            response = requests.post(self.url, json=payload, headers=self.headers, timeout=15)
            
            if response.status_code == 429:
                logger.warning("Dev.to rate limit hit (HTTP 429). Skipping Dev.to syndication for this run.")
                return False

            response.raise_for_status()
            res_data = response.json()
            logger.info(f"Successfully published article to Dev.to: {res_data.get('url')}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to Dev.to: {e}")
            return False
