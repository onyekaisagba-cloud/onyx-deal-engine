"""
Onyx Deal Engine - Main Pipeline Orchestrator
File: src/main.py
"""

import logging
from src.catalog_generator import CatalogGenerator
from src.config import Config
from src.devto_publisher import DevToPublisher
from src.fetcher import DealFetcher
from src.telegram_publisher import TelegramPublisher
from src.twitter_publisher import TwitterPublisher

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def run():
    logger.info("Starting Onyx Deal Engine pipeline execution...")

    # 1. Configuration
    config = Config.from_env()

    # 2. High-Intent Category Tuning
    fetcher = DealFetcher(
        rapidapi_key=config.RAPIDAPI_KEY, amazon_tag=config.AMAZON_TAG
    )
    deals = fetcher.fetch_tech_deals(
        categories=[
            "gaming laptop deals under 1000",
            "4k monitor price drop",
            "rtx graphics card deal",
            "ps5 gaming accessories discount",
            "noise canceling headphones deal",
        ],
        min_discount_pct=15,
        min_rating=4.0,
    )

    if not deals:
        logger.warning(
            "No deals fetched matching criteria. Exiting pipeline."
        )
        return

    logger.info(f"Retrieved {len(deals)} curated high-value deal items.")

    # 3. Dev.to Publisher
    devto = DevToPublisher(api_key=config.DEVTO_API_KEY)
    devto_success = devto.publish_roundup(deals=deals)

    # 4. Telegram Channel Publisher
    telegram_posts = 0
    if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
        telegram = TelegramPublisher(
            bot_token=config.TELEGRAM_BOT_TOKEN, chat_id=config.TELEGRAM_CHAT_ID
        )
        telegram_posts = telegram.publish_deals(deals=deals)
    else:
        logger.info(
            "Telegram credentials not configured; skipping Telegram broadcast."
        )

    # 5. X / Twitter Auto-Publisher (ADDED)
    twitter_posts = 0
    if config.TWITTER_API_KEY and config.TWITTER_API_SECRET:
        twitter = TwitterPublisher(
            api_key=config.TWITTER_API_KEY,
            api_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
        )
        twitter_posts = twitter.publish_deals(deals=deals)
    else:
        logger.info(
            "Twitter credentials not fully configured; skipping X/Twitter broadcast."
        )

    # 6. GitHub Pages Catalog Generator (FIXED METHOD CALL)
    catalog_gen = CatalogGenerator(output_path="index.html")
    catalog_success = catalog_gen.generate(deals=deals)

    logger.info(
        f"Pipeline complete. Dev.to: {devto_success} | "
        f"Telegram posts: {telegram_posts} | Twitter posts: {twitter_posts} | "
        f"HTML Catalog: {catalog_success}"
    )


if __name__ == "__main__":
    run()
