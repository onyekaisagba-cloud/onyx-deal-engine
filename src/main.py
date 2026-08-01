import logging
from src.config import Config
from src.fetcher import DealFetcher
from src.devto_publisher import DevToPublisher
from src.telegram_publisher import TelegramPublisher
from src.hashnode_publisher import HashnodePublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run():
    logger.info("Starting Onyx Deal Engine pipeline execution...")
    
    # 1. Configuration
    config = Config.from_env()
    
    # 2. Refined Deal Fetching
    fetcher = DealFetcher(rapidapi_key=config.RAPIDAPI_KEY, amazon_tag=config.AMAZON_TAG)
    deals = fetcher.fetch_tech_deals(
        categories=["gaming laptop deals", "4k monitor deals", "pc components deals", "wireless audio deals"],
        min_discount_pct=15,
        min_rating=4.0
    )
    
    if not deals:
        logger.warning("No deals fetched matching criteria. Exiting pipeline.")
        return

    logger.info(f"Retrieved {len(deals)} curated high-value deal items.")

    # 3. Dev.to Publisher
    devto = DevToPublisher(api_key=config.DEVTO_API_KEY)
    devto_success = devto.publish_roundup(deals=deals)

    # 4. Telegram Channel Publisher
    telegram = TelegramPublisher(bot_token=config.TELEGRAM_BOT_TOKEN, chat_id=config.TELEGRAM_CHAT_ID)
    telegram_posts = telegram.publish_deals(deals=deals)

    # 5. Hashnode Publisher
    hashnode = HashnodePublisher(api_key=config.HASHNODE_API_KEY, publication_id=config.HASHNODE_PUBLICATION_ID)
    hashnode_success = hashnode.publish_roundup(deals=deals)

    logger.info(
        f"Pipeline complete. Dev.to: {devto_success} | "
        f"Telegram posts: {telegram_posts} | "
        f"Hashnode: {hashnode_success}"
    )

if __name__ == "__main__":
    run()
