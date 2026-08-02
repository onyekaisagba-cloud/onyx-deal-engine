"""
Onyx Deal Engine - Amazon Bounty & Promo Manager
File: src/bounties.py
"""

import random
from typing import Dict

# Standard Amazon Bounty Landing Pages (Appends Affiliate Tag)
BOUNTY_PROMOS = {
    "US": [
        {
            "title": "Amazon Prime 30-Day Free Trial",
            "url": "https://www.amazon.com/amazonprime?primeCampaignId=prime_assoc_ft",
            "callout": "🎁 Get Free Fast Shipping & Exclusive Deals with Prime Trial!",
        },
        {
            "title": "Audible Premium Plus Free Trial",
            "url": "https://www.amazon.com/hz/audible/mlp/membership/premiumplus",
            "callout": "🎧 Get 1 Free Audiobooks with Audible 30-Day Trial!",
        },
    ],
    "CA": [
        {
            "title": "Amazon Prime Canada 30-Day Free Trial",
            "url": "https://www.amazon.ca/prime?primeCampaignId=prime_assoc_ft",
            "callout": "🇨🇦 Enjoy Fast Free Delivery & Prime Video in Canada!",
        }
    ],
}


def get_random_bounty(country: str, amazon_tag: str) -> Dict[str, str]:
    """Returns a formatted Amazon bounty promo link with affiliate tag attached."""
    promos = BOUNTY_PROMOS.get(country, BOUNTY_PROMOS["US"])
    promo = random.choice(promos)

    tag_char = "&" if "?" in promo["url"] else "?"
    affiliate_url = f"{promo['url']}{tag_char}tag={amazon_tag}"

    return {
        "title": promo["title"],
        "url": affiliate_url,
        "callout": promo["callout"],
    }
