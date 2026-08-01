import logging
import requests
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramPublisher:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def publish_deals(self, deals: List[Dict[str, Any]]) -> int:
        """Broadcasts top deals to a Telegram channel/chat."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot credentials missing. Skipping Telegram publishing.")
            return 0

        sent_count = 0
        for deal in deals[:5]:  # Top 5 deals per run
            title = deal.get("title", "Tech Deal")
            price = deal.get("price", "Limited Time Offer")
            orig = deal.get("original_price")
            rating = deal.get("rating", "N/A")
            url = deal.get("affiliate_url", "")
            img = deal.get("image_url", "")

            caption = f"🔥 <b>DEAL ALERT</b>\n\n"
            caption += f"<b>{title[:120]}...</b>\n\n"
            caption += f"💰 <b>Price:</b> {price}"
            if orig:
                caption += f" <s>({orig})</s>"
            caption += f"\n⭐ <b>Rating:</b> {rating}\n\n"
            caption += f"👉 <a href='{url}'><b>Claim Deal on Amazon</b></a>"

            try:
                if img:
                    endpoint = f"{self.base_url}/sendPhoto"
                    payload = {
                        "chat_id": self.chat_id,
                        "photo": img,
                        "caption": caption,
                        "parse_mode": "HTML"
                    }
                else:
                    endpoint = f"{self.base_url}/sendMessage"
                    payload = {
                        "chat_id": self.chat_id,
                        "text": caption,
                        "parse_mode": "HTML"
                    }

                res = requests.post(endpoint, json=payload, timeout=15)
                res.raise_for_status()
                sent_count += 1
                logger.info(f"Successfully posted Telegram deal for ASIN: {deal.get('asin')}")
            except Exception as e:
                logger.error(f"Failed to post deal to Telegram for {deal.get('asin')}: {e}")

        return sent_count
