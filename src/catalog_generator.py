import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CatalogGenerator:
    @staticmethod
    def generate_html(deals: List[Dict[str, Any]], output_path: str = "index.html") -> bool:
        """Generates a static HTML deal catalog page for GitHub Pages deployment."""
        if not deals:
            return False

        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Onyx Tech Deals - Daily High-Value Price Drops</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; color: #38bdf8; font-size: 2rem; }
        p.subtitle { text-align: center; color: #94a3b8; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .card { background: #1e293b; border-radius: 12px; padding: 20px; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #334155; }
        .card img { width: 100%; height: 180px; object-fit: contain; background: #fff; border-radius: 8px; margin-bottom: 15px; }
        .card h3 { font-size: 1rem; margin: 0 0 10px 0; color: #f1f5f9; height: 3rem; overflow: hidden; }
        .price { font-size: 1.25rem; font-weight: bold; color: #4ade80; margin-bottom: 10px; }
        .btn { display: block; text-align: center; background: #2563eb; color: #fff; text-decoration: none; padding: 10px; border-radius: 6px; font-weight: bold; }
        .btn:hover { background: #1d4ed8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Today's Curated Tech Deals</h1>
        <p class="subtitle">Automated high-value price drops updated every 6 hours.</p>
        <div class="grid">
"""

        for deal in deals:
            title = deal.get("title", "Tech Deal")
            price = deal.get("price", "Check Price")
            url = deal.get("affiliate_url", "#")
            img = deal.get("image_url", "")

            html_content += f"""
            <div class="card">
                <div>
                    {'<img src="' + img + '" alt="Product Image">' if img else ''}
                    <h3>{title}</h3>
                    <div class="price">{price}</div>
                </div>
                <a href="{url}" target="_blank" class="btn">View on Amazon</a>
            </div>
"""

        html_content += """
        </div>
    </div>
</body>
</html>
"""

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Successfully generated GitHub Pages catalog: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate HTML catalog: {e}")
            return False
