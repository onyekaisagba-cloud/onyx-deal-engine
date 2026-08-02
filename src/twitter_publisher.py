"""
Onyx Deal Engine - X / Twitter Publisher Module
File: src/twitter_publisher.py
"""

import logging
from typing import Any, Dict, List
import requests
from requests_oauthlib import OAuth1

logger = logging.getLogger(__name__)


class TwitterPublisher:

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
    ):
        self.auth = OAuth1(api_key, api_secret, access_token, access_token_secret)
        self.endpoint = "https://api.twitter.com/2/tweets"

    def publish_deals(self, deals: List[Dict[str, Any]]) -> int:
        """Publishes top high-value deals to X/Twitter."""
        if not all(self.auth.client.client_secret for _ in range(1)):
            logger.warning("Twitter API credentials incomplete. Skipping Twitter publishing.")
            return 0

        tweeted_count = 0

        for deal in deals[:3]:  # Top 3 deals per run to avoid spam limits
            title = deal.get("title", "Tech Deal")[:90]
            price = deal.get("price", "Check Link")
            badge = deal.get("badge", "🔥 HOT DEAL")
            flag = deal.get("flag", "🇺🇸")
            url = deal.get("affiliate_url", "")

            # Construct High-Engagement Tweet Copy
            tweet_text = (
                f"{flag} {badge}\n\n"
                f"{title}...\n\n"
                f"💰 Price: {price}\n"
                f"🔗 Claim Deal: {url}\n\n"
                f"#TechDeals #AmazonFinds #PCMasterRace #PriceDrop"
            )

            try:
                res = requests.post(
                    self.endpoint,
                    auth=self.auth,
                    json={"text": tweet_text},
                    timeout=15,
                )
                if res.status_code in [200, 201]:
                    tweeted_count += 1
                    logger.info(
                        f"Successfully tweeted deal for ASIN/ID: {deal.get('asin')}"
                    )
                else:
                    logger.error(
                        f"Failed to post tweet: {res.status_code} - {res.text}"
                    )
            except Exception as ex:
                logger.error(f"Exception posting tweet for {deal.get('asin')}: {ex}")

        return tweeted_count
