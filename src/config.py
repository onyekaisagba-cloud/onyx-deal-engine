"""
Onyx Deal Engine - Configuration Manager
File: src/config.py
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()


@dataclass(frozen=True)
class Config:
    # Required core configurations
    AMAZON_TAG: str
    DEVTO_API_KEY: str
    RAPIDAPI_KEY: str

    # Optional integrations (defaults to empty string if not set)
    PINTEREST_ACCESS_TOKEN: str
    PINTEREST_BOARD_ID: str
    GOOGLE_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    HASHNODE_API_KEY: str
    HASHNODE_PUBLICATION_ID: str

    # ADDED: Optional Twitter/X integration fields
    TWITTER_API_KEY: str
    TWITTER_API_SECRET: str
    TWITTER_ACCESS_TOKEN: str
    TWITTER_ACCESS_TOKEN_SECRET: str

    @classmethod
    def from_env(cls):
        """Loads environment variables and validates essential core pipeline keys."""
        amazon_tag = os.getenv("AMAZON_TAG", "onyxdeals06-20")
        devto_key = os.getenv("DEVTO_API_KEY", "")
        rapidapi_key = os.getenv("RAPIDAPI_KEY", "")

        # Optional service keys
        pinterest_token = os.getenv("PINTEREST_ACCESS_TOKEN", "")
        pinterest_board = os.getenv("PINTEREST_BOARD_ID", "tech-deals-vault")
        google_key = os.getenv("GOOGLE_API_KEY", "")

        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        telegram_chat = os.getenv("TELEGRAM_CHAT_ID", "")
        hashnode_key = os.getenv("HASHNODE_API_KEY", "")
        hashnode_pub_id = os.getenv("HASHNODE_PUBLICATION_ID", "")

        # ADDED: Optional Twitter/X credentials
        twitter_api_key = os.getenv("TWITTER_API_KEY", "")
        twitter_api_secret = os.getenv("TWITTER_API_SECRET", "")
        twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        twitter_access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

        # Strict check ONLY for core operational keys
        required_keys = {
            "DEVTO_API_KEY": devto_key,
            "RAPIDAPI_KEY": rapidapi_key,
        }

        missing = [name for name, val in required_keys.items() if not val]

        if missing:
            raise ValueError(
                f"Missing required core environment variable(s): {', '.join(missing)}"
            )

        return cls(
            AMAZON_TAG=amazon_tag,
            DEVTO_API_KEY=devto_key,
            RAPIDAPI_KEY=rapidapi_key,
            PINTEREST_ACCESS_TOKEN=pinterest_token,
            PINTEREST_BOARD_ID=pinterest_board,
            GOOGLE_API_KEY=google_key,
            TELEGRAM_BOT_TOKEN=telegram_token,
            TELEGRAM_CHAT_ID=telegram_chat,
            HASHNODE_API_KEY=hashnode_key,
            HASHNODE_PUBLICATION_ID=hashnode_pub_id,
            # ADDED: Mapping Twitter values to constructor
            TWITTER_API_KEY=twitter_api_key,
            TWITTER_API_SECRET=twitter_api_secret,
            TWITTER_ACCESS_TOKEN=twitter_access_token,
            TWITTER_ACCESS_TOKEN_SECRET=twitter_access_token_secret,
        )
