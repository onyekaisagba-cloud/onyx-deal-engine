import logging
from src.config import Config
from src.fetcher import DealFetcher
from src.devto_publisher import DevToPublisher
from src.telegram_publisher import TelegramPublisher
from src.catalog_generator import CatalogGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run():
    logger.info("Starting Onyx Deal Engine pipeline execution...")
    
    # 1. Configuration
    config = Config.from_env()
    
    # 2. High-Intent Category Tuning (Suggestion 3)
    # Search terms focused on high-intent buyers looking for specific price points & drops
    fetcher = DealFetcher(rapidapi_key=config.RAPIDAPI_KEY, amazon_tag=config.AMAZON_TAG)
    deals = fetcher.fetch_tech_deals(
        categories=[
            "gaming laptop deals under 1000", 
            "4k monitor price drop", 
            "rtx graphics card deal", 
            "ps5 gaming accessories discount",
            "noise canceling headphones deal"
        ],
        min_discount_pct=15,
        min_rating=4.0
    )
    
    if not deals:
        logger.warning("No deals fetched matching criteria. Exiting pipeline.")
        return

    logger.info(f"Retrieved {len(deals)} curated high-value deal items.")

    # 3. Dev.to Publisher (Active & Primary Blog Destination)
    devto = DevToPublisher(api_key=config.DEVTO_API_KEY)
    devto_success = devto.publish_roundup(deals=deals)

    # 4. Telegram Channel Publisher (Instant Live Channel Broadcast)
    telegram_posts = 0
    if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
        telegram = TelegramPublisher(bot_token=config.TELEGRAM_BOT_TOKEN, chat_id=config.TELEGRAM_CHAT_ID)
        telegram_posts = telegram.publish_deals(deals=deals)
    else:
        logger.info("Telegram credentials not configured; skipping Telegram broadcast.")

    # 5. GitHub Pages Catalog Generator (Suggestion 2)
    # Auto-generates index.html for zero-cost GitHub Pages deployment
    catalog_success = CatalogGenerator.generate_html(deals=deals, output_path="index.html")

    logger.info(
        f"Pipeline complete. Dev.to: {devto_success} | "
        f"Telegram posts: {telegram_posts} | HTML Catalog: {catalog_success}"
    )

if __name__ == "__main__":
    run()
