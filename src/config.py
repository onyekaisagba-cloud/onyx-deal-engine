import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

@dataclass(frozen=True)
class Config:
    AMAZON_TAG: str
    DEVTO_API_KEY: str
    RAPIDAPI_KEY: str
    PINTEREST_ACCESS_TOKEN: str
    PINTEREST_BOARD_ID: str
    GOOGLE_API_KEY: str

    @classmethod
    from_env(cls) -> "Config":
        """Loads and validates all required environment variables."""
        missing = []
        
        amazon_tag = os.getenv("AMAZON_TAG", "onyxdeals06-20")
        devto_key = os.getenv("DEVTO_API_KEY")
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        pinterest_token = os.getenv("PINTEREST_ACCESS_TOKEN")
        pinterest_board = os.getenv("PINTEREST_BOARD_ID", "tech-deals-vault")
        google_key = os.getenv("GOOGLE_API_KEY")

        keys = {
            "DEVTO_API_KEY": devto_key,
            "RAPIDAPI_KEY": rapidapi_key,
            "PINTEREST_ACCESS_TOKEN": pinterest_token,
            "GOOGLE_API_KEY": google_key,
        }

        for key_name, value in keys.items():
            if not value:
                missing.append(key_name)

        if missing:
            raise ValueError(f"Missing required environment variable(s): {', '.join(missing)}")

        return cls(
            AMAZON_TAG=amazon_tag,
            DEVTO_API_KEY=devto_key,
            RAPIDAPI_KEY=rapidapi_key,
            PINTEREST_ACCESS_TOKEN=pinterest_token,
            PINTEREST_BOARD_ID=pinterest_board,
            GOOGLE_API_KEY=google_key,
        )
