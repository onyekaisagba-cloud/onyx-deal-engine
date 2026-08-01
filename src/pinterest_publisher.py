import logging
import requests
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PinterestPublisher:
    def __init__(self, access_token: str, board_id: str):
        self.access_token = access_token
        self.board_id = board_id
        self.url = "https://api.pinterest.com/v5/pins"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def publish_deals(self, deals: List[Dict[str, Any]]) -> int:
        """Creates individual Pins for top deals on the Pinterest board."""
        successful_pins = 0

        for deal in deals[:5]:  # Post top 5 deals to prevent rate limits
            title = deal.get("title", "Tech Deal")[:100]  # Pinterest title max length
            description = f"Check out this deal: {title}. Price: {deal.get('price', 'Limited Time offer')}!"
            link = deal.get("affiliate_url")
            image_url = deal.get("image_url")

            if not link or not image_url:
                continue

            payload = {
                "board_id": self.board_id,
                "title": title,
                "description": description,
                "link": link,
                "media_source": {
                    "source_type": "image_url",
                    "url": image_url
                }
            }

            try:
                response = requests.post(self.url, json=payload, headers=self.headers, timeout=15)
                response.raise_for_status()
                successful_pins += 1
                logger.info(f"Successfully created Pinterest Pin for ASIN: {deal.get('asin')}")
            except Exception as e:
                logger.error(f"Failed to create Pin for {deal.get('asin')}: {e}")

        return successful_pins
