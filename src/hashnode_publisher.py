import logging
import requests
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HashnodePublisher:
    def __init__(self, api_key: str, publication_id: str):
        self.api_key = api_key
        self.publication_id = publication_id
        self.url = "https://gql.hashnode.com"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

    def _generate_markdown(self, deals: List[Dict[str, Any]]) -> str:
        md = "# ⚡ Tech Deals Vault — High Performance Hardware Deals\n\n"
        md += "Here are today's top curated tech deals. *Includes affiliate links.*\n\n---\n\n"

        for i, deal in enumerate(deals, 1):
            title = deal.get("title", "Tech Deal")
            price = deal.get("price", "Check site")
            orig_price = deal.get("original_price")
            rating = deal.get("rating", "N/A")
            url = deal.get("affiliate_url", "#")
            img = deal.get("image_url", "")

            md += f"### {i}. {title}\n\n"
            if img:
                md += f"![{title}]({img})\n\n"
            
            price_line = f"**Price:** `{price}`"
            if orig_price:
                price_line += f" ~~(Was {orig_price})~~"
            md += f"{price_line}\n\n"
            md += f"**Rating:** ⭐ {rating}\n\n"
            md += f"[👉 View Deal on Amazon]({url})\n\n---\n\n"

        return md

    def publish_roundup(self, deals: List[Dict[str, Any]]) -> bool:
        if not self.api_key or not self.publication_id:
            logger.warning("Hashnode credentials missing. Skipping Hashnode publishing.")
            return False

        now_str = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
        title = f"🔥 Top Tech & Hardware Deals — {now_str}"
        content = self._generate_markdown(deals)

        query = """
        mutation PublishPost($input: PublishPostInput!) {
          publishPost(input: $input) {
            post {
              id
              url
              slug
            }
          }
        }
        """

        variables = {
            "input": {
                "title": title,
                "publicationId": self.publication_id,
                "contentMarkdown": content,
                "tags": [
                    {"slug": "technology", "name": "Technology"},
                    {"slug": "hardware", "name": "Hardware"}
                ]
            }
        }

        try:
            res = requests.post(self.url, json={"query": query, "variables": variables}, headers=self.headers, timeout=15)
            res.raise_for_status()
            data = res.json()
            if "errors" in data:
                logger.error(f"Hashnode GraphQL error: {data['errors']}")
                return False
            post_url = data.get("data", {}).get("publishPost", {}).get("post", {}).get("url")
            logger.info(f"Successfully published to Hashnode: {post_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to Hashnode: {e}")
            return False
