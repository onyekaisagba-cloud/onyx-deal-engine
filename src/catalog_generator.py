"""
Onyx Deal Engine - Programmatic SEO (pSEO) Catalog & Sitemap Generator
File: src/catalog_generator.py
"""

from datetime import datetime
import html
import logging
import os
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

DOMAIN = "https://onyx-deal-engine.onrender.com"
VERIFICATION_TAG = "XrCbkESVmYJFQNyq2mqZkHoOU-S0TN5UL162TIXedPI"

# Keyword mapping to dynamically generate targeted pSEO categories
CATEGORY_MAP = {
    "gaming-laptops": ["laptop", "notebook"],
    "4k-monitors": ["monitor", "display", "screen"],
    "graphics-cards": ["graphics card", "rtx", "gpu"],
    "ps5-accessories": ["ps5", "playstation", "controller", "dualsense"],
    "noise-canceling-headphones": ["headphone", "headset", "earbuds", "airpods"],
    "budget-tech-under-100": ["under 100", "cheap", "budget", "discount"],
}


def slugify(text: str) -> str:
    """Converts a string to a clean URL slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text).strip("-")


def get_category_slug(title: str) -> str:
    """Classifies a deal title into a target pSEO category slug."""
    title_lower = title.lower()
    for slug, keywords in CATEGORY_MAP.items():
        if any(keyword in title_lower for keyword in keywords):
            return slug
    return "general-tech"


def render_html_page(title: str, subtitle: str, cards_html: str, nav_html: str) -> str:
    """Returns a full HTML template configured for conversion and Search Console indexing."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="{VERIFICATION_TAG}" />
    <title>{title} | Onyx Tech Deals</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #38bdf8; font-size: 2.2rem; margin-bottom: 5px; }}
        p.subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 25px; }}
        .nav {{ display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 30px; }}
        .nav a {{ color: #cbd5e1; text-decoration: none; background: #1e293b; padding: 6px 14px; border-radius: 20px; font-size: 0.9rem; border: 1px solid #334155; }}
        .nav a:hover, .nav a.active {{ background: #2563eb; color: #fff; border-color: #2563eb; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #334155; transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-3px); border-color: #38bdf8; }}
        .card img {{ width: 100%; height: 180px; object-fit: contain; background: #fff; border-radius: 8px; margin-bottom: 15px; }}
        .card h3 {{ font-size: 1rem; margin: 0 0 10px 0; color: #f1f5f9; height: 3rem; overflow: hidden; line-height: 1.4; }}
        .price {{ font-size: 1.3rem; font-weight: bold; color: #4ade80; margin-bottom: 15px; }}
        .btn {{ display: block; text-align: center; background: #ff9900; color: #111; text-decoration: none; padding: 12px; border-radius: 6px; font-weight: bold; transition: background 0.2s; }}
        .btn:hover {{ background: #e68a00; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
        <div class="nav">{nav_html}</div>
        <div class="grid">{cards_html}</div>
    </div>
</body>
</html>
"""


def generate_sitemap(page_paths: List[str], output_path: str = "sitemap.xml") -> bool:
    """Generates an expanded sitemap.xml covering all dynamic pSEO URLs."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    url_nodes = ""
    for path in page_paths:
        url = f"{DOMAIN}/" if path == "index.html" else f"{DOMAIN}/{path}"
        priority = "1.0" if path == "index.html" else "0.8"
        url_nodes += f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>{priority}</priority>
  </url>\n"""

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_nodes}</urlset>
"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sitemap_content)
        logger.info(f"Successfully generated pSEO sitemap with {len(page_paths)} URLs: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate sitemap: {e}")
        return False


def build_cards_html(deals: List[Dict[str, Any]]) -> str:
    """Renders card components for a subset of deal items."""
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
                    <img src="{img_url}" alt="{title}">
                    <h3>{flag} {title}</h3>
                    <div class="price">{price}</div>
                </div>
                <a href="{affiliate_url}" target="_blank" rel="nofollow sponsored" class="btn">Check Price on Amazon</a>
            </div>
        """
    return cards_html


def generate_html_catalog(deals: List[Dict[str, Any]], output_path: str = "index.html") -> bool:
    """Builds index.html alongside category-specific pSEO sub-pages and updates sitemap.xml."""
    if not os.path.exists("deals"):
        os.makedirs("deals", exist_ok=True)

    # 1. Group deals into category buckets
    categorized_deals: Dict[str, List[Dict[str, Any]]] = {}
    for deal in deals:
        slug = get_category_slug(deal.get("title", ""))
        categorized_deals.setdefault(slug, []).append(deal)

    # 2. Construct navigation bar HTML
    nav_links = [f'<a href="{DOMAIN}/" class="active">🔥 All Deals</a>']
    for slug in categorized_deals.keys():
        category_title = slug.replace("-", " ").title()
        nav_links.append(f'<a href="{DOMAIN}/deals/{slug}.html">{category_title}</a>')
    nav_html = "".join(nav_links)

    generated_files = [output_path]

    # 3. Generate category pages under /deals/
    for slug, cat_deals in categorized_deals.items():
        category_title = slug.replace("-", " ").title()
        cat_file_path = os.path.join("deals", f"{slug}.html")
        cat_cards = build_cards_html(cat_deals)
        
        cat_html = render_html_page(
            title=f"Best {category_title} Price Drops",
            subtitle=f"Automated top-rated {category_title.lower()} offers updated daily.",
            cards_html=cat_cards,
            nav_html=nav_html
        )
        
        with open(cat_file_path, "w", encoding="utf-8") as f:
            f.write(cat_html)
        generated_files.append(cat_file_path.replace("\\", "/"))

    # 4. Generate Root index.html
    main_cards = build_cards_html(deals)
    main_html = render_html_page(
        title="🔥 Today's Curated Tech Deals",
        subtitle="Automated high-value price drops updated every 6 hours.",
        cards_html=main_cards,
        nav_html=nav_html
    )

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(main_html)
        logger.info(f"Successfully generated main index and {len(generated_files) - 1} pSEO category pages.")

        # 5. Rebuild sitemap covering all generated pSEO paths
        generate_sitemap(generated_files, "sitemap.xml")
        return True
    except Exception as e:
        logger.error(f"Failed to generate catalog pipeline: {e}")
        return False


class CatalogGenerator:
    """Class wrapper providing object interface for catalog generation."""

    def __init__(self, output_path: str = "index.html"):
        self.output_path = output_path

    def generate(self, deals: List[Dict[str, Any]]) -> bool:
        """Triggers multi-page HTML catalog generation."""
        return generate_html_catalog(deals, self.output_path)

    @staticmethod
    def generate_sitemap(page_paths: List[str], output_path: str = "sitemap.xml") -> bool:
        """Triggers sitemap generation."""
        return generate_sitemap(page_paths, output_path)
