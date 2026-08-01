import logging
from src.config import Config
from src.fetcher import DealFetcher
from src.devto_publisher import DevToPublisher
from src.telegram_publisher import TelegramPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run():
    logger.info("Starting Onyx Deal Engine pipeline execution...")
    
    # 1. Configuration
    config = Config.from_env()
    
    # 2. High-Ticket / High-Value Deal Fetching
    fetcher = DealFetcher(rapidapi_key=config.RAPIDAPI_KEY, amazon_tag=config.AMAZON_TAG)
    deals = fetcher.fetch_tech_deals(
        categories=[
            "rtx gaming laptop deals", 
            "4k oled monitor deals", 
            "graphics card gpu deals", 
            "desktop pc components deals",
            "premium noise canceling headphones"
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

    logger.info(
        f"Pipeline complete. Dev.to: {devto_success} | "
        f"Telegram posts: {telegram_posts}"
    )

if __name__ == "__main__":
    run()
