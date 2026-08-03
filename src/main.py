"""
Onyx Deal Engine - Main Pipeline Orchestrator (Revenue Optimized)
File: src/main.py
"""

import logging
from src.catalog_generator import CatalogGenerator
from src.config import Config
from src.devto_publisher import DevToPublisher
from src.fetcher import DealFetcher
from src.telegram_publisher import TelegramPublisher

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def run():
    logger.info("Starting Onyx Deal Engine revenue-optimized pipeline execution...")

    # 1. Configuration
    config = Config.from_env()

    # 2. High-Yield & High-AOV Category Ingestion
    fetcher = DealFetcher(
        rapidapi_key=config.RAPIDAPI_KEY, amazon_tag=config.AMAZON_TAG
    )
    deals = fetcher.fetch_tech_deals(
        categories=[
            "rtx 4070 gaming laptop deal",
            "oled gaming monitor discount",
            "rtx 4080 graphics card price drop",
            "ps5 portal accessories deal",
            "wireless noise canceling headphones deal",
            "portable gaming handheld deal",
        ],
        min_discount_pct=10,
        min_rating=4.0,
    )

    if not deals:
        logger.warning(
            "No deals fetched matching criteria. Exiting pipeline."
        )
        return

    logger.info(f"Retrieved {len(deals)} curated high-yield deal items.")

    # 3. Dev.to Publisher (High-CTR SEO Syndication)
    devto = DevToPublisher(api_key=config.DEVTO_API_KEY)
    devto_success = devto.publish_roundup(deals=deals)

    # 4. Telegram Internal Diagnostic & Logging Feed
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

    # 5. X / Twitter (Disabled - Zero-Cost Mode)
    twitter_posts = 0

    # 6. Multi-Page pSEO Catalog & Sitemap Generator
    catalog_gen = CatalogGenerator(output_path="index.html")
    catalog_success = catalog_gen.generate(deals=deals)

    logger.info(
        f"Revenue Pipeline complete. Dev.to: {devto_success} | "
        f"Telegram posts: {telegram_posts} | HTML Catalog & pSEO: {catalog_success}"
    )


if __name__ == "__main__":
    run()
