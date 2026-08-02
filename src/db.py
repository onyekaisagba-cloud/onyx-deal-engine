"""
Onyx Deal Engine - Price Tracking & Badging Database
File: src/db.py
"""

import sqlite3
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)
DB_PATH = "onyx_deals.db"


def init_db():
    """Initializes the SQLite tables for tracking historical ASIN prices."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS price_history (
                asin TEXT,
                country TEXT,
                price REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (asin, country, timestamp)
            )
        """
        )
        conn.commit()


def process_price_badge(
    asin: str, country: str, current_price: float
) -> Tuple[Optional[str], Optional[float]]:
    """
    Compares current_price against historical records.
    Returns a tuple: (badge_label, lowest_recorded_price).
    """
    if not current_price or current_price <= 0:
        return None, None

    init_db()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Fetch minimum historical price
        cursor.execute(
            "SELECT MIN(price) FROM price_history WHERE asin = ? AND country = ?",
            (asin, country),
        )
        result = cursor.fetchone()
        min_price = result[0] if result and result[0] is not None else None

        badge = None
        if min_price is None:
            badge = "✨ NEW DEAL"
        elif current_price < min_price:
            badge = "🔥 ALL-TIME LOW"
        elif current_price <= min_price * 1.02:
            badge = "⚡ NEAR HISTORICAL LOW"

        # Record current price
        cursor.execute(
            "INSERT INTO price_history (asin, country, price) VALUES (?, ?, ?)",
            (asin, country, current_price),
        )
        conn.commit()

        return badge, min_price
