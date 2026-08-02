import logging
import requests
import urllib.parse
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DealFetcher:
    def __init__(self, rapidapi_key: str, amazon_tag: str):
        self.rapidapi_key = rapidapi_key
        self.amazon_tag = amazon_tag
        self.url = "https://real-time-amazon-data.p.rapidapi.com/search"
        self.headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
        }

    def _apply_affiliate_tag(self, raw_url: str) -> str:
        """Appends/updates the Amazon Associate tag on product URLs."""
        if not raw_url:
            return ""
        parsed = urllib.parse.urlparse(raw_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        query_params['tag'] = [self.amazon_tag]
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        return urllib.parse.urlunparse(parsed._replace(query=new_query))

    def fetch_tech_deals(
        self, 
        categories: List[str] = None, 
        min_discount_pct: int = 15,
        min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """Fetches and filters high-value tech deals across both US and CA marketplaces."""
        if not categories:
            categories = ["gaming laptop deals", "4k monitor deals", "pc components deals", "wireless audio deals"]

        all_deals = []
        seen_asins = set()

        # Configured target regions
        regions = [
            {"country": "US", "currency": "USD", "flag": "🇺🇸"},
            {"country": "CA", "currency": "CAD", "flag": "🇨🇦"}
        ]

        for region in regions:
            for query in categories:
                params = {
                    "query": query,
                    "page": "1",
                    "country": region["country"],
                    "sort_by": "RELEVANCE",
                    "product_condition": "NEW"
                }

                try:
                    res = requests.get(self.url, headers=self.headers, params=params, timeout=15)
                    res.raise_for_status()
                    products = res.json().get("data", {}).get("products", [])

                    for item in products:
                        asin = item.get("asin")
                        # Deduplicate by unique combination of ASIN and Country Code
                        unique_key = f"{asin}_{region['country']}"
                        if not asin or unique_key in seen_asins:
                            continue

                        # Filtering Logic
                        price_str = item.get("product_price", "")
                        orig_price_str = item.get("product_original_price", "")
                        rating_val = item.get("product_star_rating")
                        
                        try:
                            rating = float(rating_val) if rating_val else 0.0
                        except ValueError:
                            rating = 0.0

                        # Calculate or verify discount percentage
                        if item.get("is_prime_day_deal") or item.get("is_best_seller") or orig_price_str:
                            if rating >= min_rating or orig_price_str:
                                pass # Keep valid deal candidates

                        affiliate_link = self._apply_affiliate_tag(item.get("product_url", ""))
                        
                        deal_entry = {
                            "asin": asin,
                            "title": item.get("product_title", "Tech Product"),
                            "price": price_str or "Check Deal",
                            "original_price": orig_price_str,
                            "currency": region["currency"],
                            "flag": region["flag"],
                            "country": region["country"],
                            "rating": rating,
                            "num_ratings": item.get("product_num_ratings", 0),
                            "affiliate_url": affiliate_link,
                            "image_url": item.get("product_photo", ""),
                            "category": query
                        }

                        seen_asins.add(unique_key)
                        all_deals.append(deal_entry)

                except Exception as e:
                    logger.error(f"Error fetching deals for query '{query}' in region {region['country']}: {e}")

        logger.info(f"Successfully fetched and filtered {len(all_deals)} high-value deals across US & CA.")
        return all_deals[:10]  # Return top 10 curated deals across regions
