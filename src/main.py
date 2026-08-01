import logging
from src.config import Config
from src.fetcher import DealFetcher
from src.devto_publisher import DevToPublisher
from src.pinterest_publisher import PinterestPublisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run():
    logger.info("Starting Onyx Deal Engine pipeline execution...")
    
    # 1. Load Configuration
    config = Config.from_env()
    
    # 2. Fetch Deals
    fetcher = DealFetcher(rapidapi_key=config.RAPIDAPI_KEY, amazon_tag=config.AMAZON_TAG)
    deals = fetcher.fetch_tech_deals(query="tech deals")
    
    if not deals:
        logger.warning("No deals fetched. Exiting pipeline.")
        return

    logger.info(f"Retrieved {len(deals)} formatted deal items.")

    # 3. Dev.to Article Publishing (Let publisher handle dynamic timestamp title)
    devto = DevToPublisher(api_key=config.DEVTO_API_KEY)
    devto_success = devto.publish_roundup(deals=deals)

    # 4. Pinterest Pin Publishing (Safe Wrapper)
    pins_created = 0
    try:
        pinterest = PinterestPublisher(
            access_token=config.PINTEREST_ACCESS_TOKEN, 
            board_id=config.PINTEREST_BOARD_ID
        )
        pins_created = pinterest.publish_deals(deals)
    except Exception as e:
        logger.warning(f"Pinterest publishing skipped: {e}")

    logger.info(f"Pipeline complete. Dev.to published: {devto_success} | Pinterest pins created: {pins_created}")

if __name__ == "__main__":
    run()
