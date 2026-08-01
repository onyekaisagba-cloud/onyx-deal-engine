import logging
import requests
from typing import List, Dict, Any
from src.link_transformer import attach_associate_tag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DealFetcher:
    def __init__(self, rapidapi_key: str, amazon_tag: str):
        self.rapidapi_key = rapidapi_key
        self.amazon_tag = amazon_tag
        self.headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
        }

    def fetch_tech_deals(self, category_id: str = "aps", query: str = "tech deals") -> List[Dict[str, Any]]:
        """
        Fetches active deal products from RapidAPI Amazon endpoint.
        """
        url = "https://real-time-amazon-data.p.rapidapi.com/search"
        params = {
            "query": query,
            "page": "1",
            "country": "US",
            "sort_by": "RELEVANCE",
            "product_condition": "ALL"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            products = data.get("data", {}).get("products", [])
            processed_deals = []

            for item in products[:10]:  # Cap to top 10 relevant deals
                raw_url = item.get("product_url", "")
                affiliate_url = attach_associate_tag(raw_url, self.amazon_tag)

                deal = {
                    "asin": item.get("asin"),
                    "title": item.get("product_title"),
                    "price": item.get("product_price"),
                    "original_price": item.get("product_original_price"),
                    "rating": item.get("product_star_rating"),
                    "num_ratings": item.get("product_num_ratings"),
                    "image_url": item.get("product_photo"),
                    "affiliate_url": affiliate_url,
                    "is_prime": item.get("is_prime", False)
                }
                processed_deals.append(deal)

            logger.info(f"Successfully fetched and transformed {len(processed_deals)} deals.")
            return processed_deals

        except Exception as e:
            logger.error(f"Failed to fetch deals: {e}")
            return []
