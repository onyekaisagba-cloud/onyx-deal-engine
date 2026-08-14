"""
Onyx Deal Engine - Programmatic SEO (pSEO) Catalog & Sitemap Generator
File: src/catalog_generator.py
"""

from datetime import datetime
import html
import json
import logging
import os
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

DOMAIN = "https://onyx-deal-engine.onrender.com"
VERIFICATION_TAG = "XrCbkESVmYJFQNyq2mqZkHoOU-S0TN5UL162TIXedPI"

# Expanded Multi-Industry pSEO Keyword Mapping (Year-Round Revenue Optimization)
CATEGORY_MAP = {
    # -------------------------------------------------------------------------
    # 1. High-Margin Digital & Evergreen (365-Day Recurring Income: 15% - 40%)
    # -------------------------------------------------------------------------
    "saas-ai-tools": ["ai", "gpt", "saas", "software", "copilot", "prompt", "api"],
    "hosting-cloud-deals": ["hosting", "server", "domain", "cloud", "vps", "wordpress"],
    "vpn-privacy-security": ["vpn", "antivirus", "security", "password", "privacy"],

    # -------------------------------------------------------------------------
    # 2. High-Frequency Retail & Apparel (High Checkout Velocity)
    # -------------------------------------------------------------------------
    "trending-fashion-apparel": ["shirt", "shoes", "sneakers", "hoodie", "apparel", "dress", "jacket", "wear"],
    "designer-watches-accessories": ["watch", "jewelry", "bag", "sunglasses", "backpack", "wallet"],

    # -------------------------------------------------------------------------
    # 3. Travel & Hospitality (Spring / Summer Peak Season Offset)
    # -------------------------------------------------------------------------
    "flight-hotel-discounts": ["hotel", "flight", "resort", "airline", "vacation", "booking", "stay"],
    "luggage-travel-gear": ["luggage", "suitcase", "travel", "carry-on", "duffel"],

    # -------------------------------------------------------------------------
    # 4. Health, Fitness & New Year Surge (Q1 Spending Peak)
    # -------------------------------------------------------------------------
    "fitness-workout-gear": ["gym", "workout", "dumbbells", "treadmill", "fitness", "activewear"],
    "health-supplements-wellness": ["protein", "vitamin", "supplement", "creatine", "wellness"],

    # -------------------------------------------------------------------------
    # 5. Core Consumer Tech & Gaming (Q4 Holiday Peak)
    # -------------------------------------------------------------------------
    "rtx-gaming-laptops": ["laptop", "notebook", "rtx", "macbook"],
    "4k-oled-monitors": ["monitor", "display", "screen", "oled"],
    "graphics-cards-gpus": ["graphics card", "rtx", "gpu", "radeon"],
    "ps5-console-accessories": ["ps5", "playstation", "xbox", "controller", "dualsense", "portal"],
    "noise-canceling-audio": ["headphone", "headset", "earbuds", "airpods", "speaker", "soundbar"],
    "handheld-gaming-pcs": ["handheld", "deck", "rog", "ally", "switch"],
    "gaming-mice-keyboards": ["keyboard", "mouse", "keycap", "mousepad"],
    "fast-ssd-storage": ["ssd", "nvme", "storage", "drive", "hard drive"],
    "smart-home-automation": ["smart", "plug", "alexa", "echo", "ring", "nest"],

    # -------------------------------------------------------------------------
    # 6. Intent-Based Budget Buckets (High Search Conversion Rates)
    # -------------------------------------------------------------------------
    "budget-deals-under-50": ["under 50", "cheap", "under $50"],
    "budget-deals-under-100": ["under 100", "under $100"],
    "premium-flagship-deals": ["pro", "ultra", "max", "flagship", "edition"]
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


def render_html_page(title: str, subtitle: str, cards_html: str, nav_html: str, deals: List[Dict[str, Any]] = None) -> str:
    """Returns a full HTML template configured for conversion, Search Console indexing, JSON-LD structured data, and Amazon policy compliance."""
    
    # Generate Schema.org ItemList JSON-LD structured data for Google Rich Snippets
    json_ld_items = []
    if deals:
        for idx, deal in enumerate(deals[:10], start=1):
            clean_price = re.sub(r"[^\d.]", "", str(deal.get("price", "0.00"))) or "0.00"
            json_ld_items.append({
                "@type": "ListItem",
                "position": idx,
                "item": {
                    "@type": "Product",
                    "name": deal.get("title", "Tech Deal"),
                    "image": deal.get("image_url", ""),
                    "offers": {
                        "@type": "Offer",
                        "priceCurrency": "USD",
                        "price": clean_price,
                        "availability": "https://schema.org/InStock",
                        "url": deal.get("affiliate_url", DOMAIN)
                    }
                }
            })
    
    json_ld_script = ""
    if json_ld_items:
        structured_data = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "itemListElement": json_ld_items
        }
        json_ld_script = f'<script type="application/ld+json">\n{json.dumps(structured_data, indent=2)}\n</script>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="{VERIFICATION_TAG}" />
    <title>{title} | Onyx Tech Deals</title>
    {json_ld_script}
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
        footer {{ margin-top: 50px; text-align: center; color: #64748b; font-size: 0.85rem; border-top: 1px solid #334155; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
        <div class="nav">{nav_html}</div>
        <div class="grid">{cards_html}</div>
        <footer>
            <p>As an Amazon Associate I earn from qualifying purchases.</p>
        </footer>
    </div>
</body>
</html>
"""


def generate_sitemap(page_paths: List[str], output_path: str = "sitemap.xml") -> bool:
    """Generates an expanded sitemap.xml with strict Line 1 Column 1 XML declaration."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    url_nodes = []
    for path in page_paths:
        url = f"{DOMAIN}/" if path == "index.html" else f"{DOMAIN}/{path}"
        priority = "1.0" if path == "index.html" else "0.8"
        url_nodes.append(
            f"  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>daily</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )

    nodes_str = "\n".join(url_nodes)
    
    # Clean string construction without leading newline
    sitemap_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{nodes_str}\n'
        '</urlset>'
    )

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sitemap_content)
        logger.info(f"Successfully generated clean XML sitemap with {len(page_paths)} URLs: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate sitemap: {e}")
        return False


def build_cards_html(deals: List[Dict[str, Any]]) -> str:
    """Renders high-conversion card components with dynamic price badges and callouts."""
    cards_html = ""
    for deal in deals:
        title = html.escape(deal.get("title", "Tech Deal"))
        price = html.escape(str(deal.get("price", "$0.00")))
        orig_price = deal.get("original_price")
        discount_pct = deal.get("discount_percentage", 0)
        img_url = deal.get("image_url", "")
        affiliate_url = deal.get("affiliate_url", "#")
        flag = deal.get("flag", "🇺🇸")

        if orig_price and str(orig_price).strip() not in ["None", ""]:
            badge_html = f'<span style="background: #ef4444; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-bottom: 8px; display: inline-block;">SAVE {int(discount_pct)}%</span>'
            orig_price_html = f'<span style="text-decoration: line-through; color: #64748b; font-size: 0.9rem; margin-left: 8px;">{orig_price}</span>'
        else:
            badge_html = '<span style="background: #22c55e; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-bottom: 8px; display: inline-block;">VERIFIED DEAL</span>'
            orig_price_html = ""

        cards_html += f"""
            <div class="card">
                <div>
                    {badge_html}
                    <img src="{img_url}" alt="{title}">
                    <h3>{flag} {title}</h3>
                    <div class="price">{price} {orig_price_html}</div>
                </div>
                <a href="{affiliate_url}" target="_blank" rel="nofollow sponsored" class="btn">⚡ Grab This Deal on Amazon</a>
            </div>
        """
    return cards_html


def export_json_api(deals: List[Dict[str, Any]], output_path: str = "deals.json") -> bool:
    """Exports structured JSON data for Chrome/Edge browser extensions."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"updated_at": datetime.utcnow().isoformat(), "count": len(deals), "deals": deals}, f, indent=2)
        logger.info(f"Exported browser extension API feed to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export JSON API feed: {e}")
        return False


def generate_html_catalog(deals: List[Dict[str, Any]], output_path: str = "index.html") -> bool:
    """Builds index.html alongside category-specific pSEO sub-pages, exports extension API JSON, and updates sitemap.xml."""
    if not os.path.exists("deals"):
        os.makedirs("deals", exist_ok=True)

    categorized_deals: Dict[str, List[Dict[str, Any]]] = {}
    for deal in deals:
        slug = get_category_slug(deal.get("title", ""))
        categorized_deals.setdefault(slug, []).append(deal)

    nav_links = [f'<a href="{DOMAIN}/" class="active">🔥 All Deals</a>']
    for slug in categorized_deals.keys():
        category_title = slug.replace("-", " ").title()
        nav_links.append(f'<a href="{DOMAIN}/deals/{slug}.html">{category_title}</a>')
    nav_html = "".join(nav_links)

    generated_files = [output_path]

    for slug, cat_deals in categorized_deals.items():
        category_title = slug.replace("-", " ").title()
        cat_file_path = os.path.join("deals", f"{slug}.html")
        cat_cards = build_cards_html(cat_deals)
        
        cat_html = render_html_page(
            title=f"Best {category_title} Price Drops",
            subtitle=f"Automated top-rated {category_title.lower()} offers updated daily.",
            cards_html=cat_cards,
            nav_html=nav_html,
            deals=cat_deals
        )
        
        with open(cat_file_path, "w", encoding="utf-8") as f:
            f.write(cat_html)
        generated_files.append(cat_file_path.replace("\\", "/"))

    main_cards = build_cards_html(deals)
    main_html = render_html_page(
        title="🔥 Today's Curated Tech Deals",
        subtitle="Automated high-value price drops updated every 6 hours.",
        cards_html=main_cards,
        nav_html=nav_html,
        deals=deals
    )

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(main_html)
        
        # Rebuild sitemap & extension API feed
        generate_sitemap(generated_files, "sitemap.xml")
        export_json_api(deals, "deals.json")
        return True
    except Exception as e:
        logger.error(f"Failed to generate catalog pipeline: {e}")
        return False


class CatalogGenerator:
    """Class wrapper providing object interface for catalog generation."""

    def __init__(self, output_path: str = "index.html"):
        self.output_path = output_path

    def generate(self, deals: List[Dict[str, Any]]) -> bool:
        return generate_html_catalog(deals, self.output_path)

    @staticmethod
    def generate_sitemap(page_paths: List[str], output_path: str = "sitemap.xml") -> bool:
        return generate_sitemap(page_paths, output_path)
