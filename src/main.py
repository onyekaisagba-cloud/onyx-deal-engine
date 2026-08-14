"""
Onyx Deal Engine - Main Pipeline Orchestrator (Revenue & Multi-Industry Optimized)
File: src/main.py
"""

import logging
from typing import Any, Dict, List
from src.catalog_generator import CatalogGenerator, get_category_slug
from src.config import Config
from src.devto_publisher import DevToPublisher
from src.fetcher import DealFetcher
from src.link_transformer import attach_associate_tag
from src.telegram_publisher import TelegramPublisher

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Expanded Multi-Industry Query Grid
MULTI_INDUSTRY_CATEGORIES = [
    # 1. Core Tech & Hardware
    "rtx 4070 gaming laptop deal",
    "oled gaming monitor price drop",
    "rtx 4080 graphics card discount",
    "ps5 portal accessories deal",
    "wireless noise canceling headphones sale",
    "portable gaming handheld deal",
    "mechanical gaming keyboard mouse deal",
    "nvme ssd storage price drop",
    "smart home tech deals",
    
    # 2. Digital, SaaS & Security
    "software subscription deals",
    "antivirus security software deals",
    "cloud storage subscription deals",

    # 3. High-Frequency Fashion & Accessories
    "men women sneakers apparel sale",
    "designer watches sale",
    "backpacks travel bags sale",

    # 4. Travel & Hospitality Gear
    "travel carry on luggage deals",
    "travel neck pillow packing cubes deals",

    # 5. Health, Fitness & Wellness
    "workout gym gear deals",
    "protein whey supplement deals",
    "fitness smartwatch deals",

    # 6. Intent & Budget Buckets
    "budget tech deals under 50",
    "budget tech deals under 100",
    "premium pro tech deals"
]

# Curated Fallback Deals to Guarantee 0 Blank Categories Across All Pages
FALLBACK_DEALS = [
    {
        "title": "Microsoft 365 Personal 12-Month Auto-Renew Subscription",
        "price": "$69.99",
        "original_price": "$79.99",
        "discount_percentage": 12,
        "image_url": "https://m.media-amazon.com/images/I/61f22v+i2EL._AC_SL1500_.jpg",
        "affiliate_url": attach_associate_tag("https://www.amazon.com/dp/B0863TX4S3"),
        "flag": "🇺🇸"
    },
    {
        "title": "Samsonite Omnia Hardside Expandable Luggage 2-Piece Set",
        "price": "$189.00",
        "original_price": "$249.99",
        "discount_percentage": 24,
        "image_url": "https://m.media-amazon.com/images/I/81P8j2b4n2L._AC_SL1500_.jpg",
        "affiliate_url": attach_associate_tag("https://www.amazon.com/dp/B013WF1T3U"),
        "flag": "🇺🇸"
    },
    {
        "title": "Optimum Nutrition Gold Standard 100% Whey Protein Powder 5 lb",
        "price": "$74.99",
        "original_price": "$85.00",
        "discount_percentage": 11,
        "image_url": "https://m.media-amazon.com/images/I/7162y05zH2L._AC_SL1500_.jpg",
        "affiliate_url": attach_associate_tag("https://www.amazon.com/dp/B000QSNYGI"),
        "flag": "🇺🇸"
    },
    {
        "title": "Nike Air Max 270 Men's Athletic Running Shoes",
        "price": "$129.95",
        "original_price": "$160.00",
        "discount_percentage": 18,
        "image_url": "https://m.media-amazon.com/images/I/61NfI0c-T1L._AC_UY695_.jpg",
        "affiliate_url": attach_associate_tag("https://www.amazon.com/dp/B078864XQL"),
        "flag": "🇺🇸"
    }
]


def run():
    logger.info("Starting Onyx Deal Engine revenue-optimized pipeline execution...")

    # 1. Configuration
    config = Config.from_env()

    # 2. Multi-Industry Ingestion via DealFetcher & Native Scraper
    deals: List[Dict[str, Any]] = []

    # 2a. Primary Fetcher (RapidAPI / Amazon Tag Ingestion)
    try:
        fetcher = DealFetcher(
            rapidapi_key=config.RAPIDAPI_KEY, amazon_tag=config.AMAZON_TAG
        )
        fetched_deals = fetcher.fetch_tech_deals(
            categories=MULTI_INDUSTRY_CATEGORIES,
            min_discount_pct=10,
            min_rating=4.0,
        )
        if fetched_deals:
            deals.extend(fetched_deals)
    except Exception as err:
        logger.warning(f"DealFetcher ingestion notice: {err}")

    # 2b. Native Amazon Multi-Category Sweeper Fallback
    try:
        from src.scrapers.amazon import fetch_amazon_deals
        native_deals = fetch_amazon_deals(region="US", amazon_tag=config.AMAZON_TAG)
        if native_deals:
            deals.extend(native_deals)
    except Exception as err:
        logger.warning(f"Native Amazon scraper notice: {err}")

    # 2c. Backfill Missing Categories with Curated Seed Deals (Guarantees 0 Blank Sub-Pages)
    existing_categories = {get_category_slug(d.get("title", "")) for d in deals}
    for fallback in FALLBACK_DEALS:
        slug = get_category_slug(fallback.get("title", ""))
        if slug not in existing_categories:
            deals.append(fallback)
            existing_categories.add(slug)

    if not deals:
        logger.warning("No deals collected across pipelines. Exiting execution cycle.")
        return

    logger.info(f"Retrieved total of {len(deals)} curated multi-industry deal items.")

    # 3. Dev.to Publisher (High-CTR SEO Syndication)
    devto = DevToPublisher(api_key=config.DEVTO_API_KEY)
    devto_success = devto.publish_roundup(deals=deals)

    # 4. Telegram Direct Feed
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

    # 6. Multi-Page pSEO Catalog, Sitemap, & Extension JSON Feed Generator
    catalog_gen = CatalogGenerator(output_path="index.html")
    catalog_success = catalog_gen.generate(deals=deals)

    logger.info(
        f"Revenue Pipeline complete. Dev.to: {devto_success} | "
        f"Telegram posts: {telegram_posts} | HTML Catalog & pSEO: {catalog_success}"
    )


if __name__ == "__main__":
    run()
