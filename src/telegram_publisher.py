import html
import logging
import requests
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramPublisher:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = str(chat_id).strip()
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def publish_deals(self, deals: List[Dict[str, Any]]) -> int:
        """Broadcasts top deals to a Telegram channel/chat with safe fallback handling."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot credentials missing. Skipping Telegram publishing.")
            return 0

        sent_count = 0
        for deal in deals[:5]:  # Top 5 deals per run
            raw_title = deal.get("title", "Tech Deal")
            safe_title = html.escape(raw_title[:100])
            
            price = html.escape(str(deal.get("price", "Limited Time Offer")))
            currency = deal.get("currency", "USD")
            flag = deal.get("flag", "🇺🇸")
            orig = deal.get("original_price")
            rating = str(deal.get("rating", "N/A"))
            url = html.escape(deal.get("affiliate_url", ""))
            img = deal.get("image_url", "")

            caption = f"🔥 <b>DEAL ALERT</b> {flag}\n\n"
            caption += f"<b>{safe_title}...</b>\n\n"
            caption += f"💰 <b>Price:</b> {price} {currency}"
            if orig:
                caption += f" <s>({html.escape(str(orig))})</s>"
            caption += f"\n⭐ <b>Rating:</b> {rating}\n\n"
            caption += f"👉 <a href=\"{url}\"><b>Claim Deal on Amazon</b></a>\n\n"
            caption += f"<i>*Prices listed in {currency}. Amazon OneLink auto-redirects international visitors to local storefronts.</i>"

            success = False
            # Try sendPhoto
            if img:
                try:
                    photo_payload = {
                        "chat_id": self.chat_id,
                        "photo": img,
                        "caption": caption,
                        "parse_mode": "HTML"
                    }
                    res = requests.post(f"{self.base_url}/sendPhoto", json=photo_payload, timeout=15)
                    res.raise_for_status()
                    success = True
                except requests.exceptions.HTTPError as e:
                    err_msg = e.response.text if e.response is not None else str(e)
                    logger.warning(f"sendPhoto failed for {deal.get('asin')}: {err_msg}. Retrying with sendMessage...")
                except Exception as e:
                    logger.warning(f"sendPhoto exception for {deal.get('asin')}: {e}")

            # Try sendMessage fallback
            if not success:
                try:
                    msg_payload = {
                        "chat_id": self.chat_id,
                        "text": caption,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": False
                    }
                    res = requests.post(f"{self.base_url}/sendMessage", json=msg_payload, timeout=15)
                    res.raise_for_status()
                    success = True
                except requests.exceptions.HTTPError as e:
                    err_msg = e.response.text if e.response is not None else str(e)
                    logger.error(f"Failed to post deal to Telegram for {deal.get('asin')}: {err_msg}")
                except Exception as e:
                    logger.error(f"Failed to post deal to Telegram for {deal.get('asin')}: {e}")

            if success:
                sent_count += 1
                logger.info(f"Successfully posted Telegram deal for ASIN: {deal.get('asin')} ({deal.get('country')})")

        return sent_count
