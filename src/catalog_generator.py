"""
Onyx Deal Engine - Catalog & Sitemap Generator
File: src/catalog_generator.py
"""

from datetime import datetime
import html
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def generate_sitemap(output_path: str = "sitemap.xml") -> bool:
    """Generates a valid sitemap.xml for Search Console indexing."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://onyekaisagba-cloud.github.io/onyx-deal-engine/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sitemap_content)
        logger.info(f"Successfully generated sitemap: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate sitemap: {e}")
        return False


def generate_html_catalog(
    deals: List[Dict[str, Any]], output_path: str = "index.html"
) -> bool:
    """Generates index.html catalog and associated sitemap.xml."""
    # Generate HTML Storefront
    cards_html = ""
    for deal in deals:
        title = html.escape(deal.get("title", "Tech Deal"))
        price = html.escape(str(deal.get("price", "$0.00")))
        img_url = deal.get("image_url", "")
        affiliate_url = deal.get("affiliate_url", "#")
        flag = deal.get("flag", "🇺🇸")

        cards_html += f"""
            <div class="card">
                <div>
                    <img src="{img_url}" alt="Product Image">
                    <h3>{flag} {title}</h3>
                    <div class="price">{price}</div>
                </div>
                <a href="{affiliate_url}" target="_blank" class="btn">View on Amazon</a>
            </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="vUJO5ZYWYpCMsOBQQ6uGElWMqdq5GhBdYDXb-XtD2ac" />
    <title>Onyx Tech Deals - Daily High-Value Price Drops</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #38bdf8; font-size: 2rem; }}
        p.subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #334155; }}
        .card img {{ width: 100%; height: 180px; object-fit: contain; background: #fff; border-radius: 8px; margin-bottom: 15px; }}
        .card h3 {{ font-size: 1rem; margin: 0 0 10px 0; color: #f1f5f9; height: 3rem; overflow: hidden; }}
        .price {{ font-size: 1.25rem; font-weight: bold; color: #4ade80; margin-bottom: 10px; }}
        .btn {{ display: block; text-align: center; background: #2563eb; color: #fff; text-decoration: none; padding: 10px; border-radius: 6px; font-weight: bold; }}
        .btn:hover {{ background: #1d4ed8; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Today's Curated Tech Deals</h1>
        <p class="subtitle">Automated high-value price drops updated every 6 hours.</p>
        <div class="grid">
            {cards_html}
        </div>
    </div>
</body>
</html>
"""

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Successfully generated HTML catalog: {output_path}")

        # Always build sitemap alongside catalog
        generate_sitemap("sitemap.xml")
        return True
    except Exception as e:
        logger.error(f"Failed to generate catalog: {e}")
        return False


# Added Class Wrapper to satisfy `from src.catalog_generator import CatalogGenerator`
class CatalogGenerator:
    """Class wrapper providing object interface for catalog generation."""

    def __init__(self, output_path: str = "index.html"):
        self.output_path = output_path

    def generate(self, deals: List[Dict[str, Any]]) -> bool:
        """Triggers HTML catalog generation."""
        return generate_html_catalog(deals, self.output_path)

    @staticmethod
    def generate_sitemap(output_path: str = "sitemap.xml") -> bool:
        """Triggers sitemap generation."""
        return generate_sitemap(output_path)
