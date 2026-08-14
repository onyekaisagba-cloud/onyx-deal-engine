"""
Onyx Deal Engine - Link Transformation Service
File: src/link_transformer.py
"""

import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


def extract_asin(url: str) -> str:
    """Extracts a 10-character Amazon ASIN from various Amazon URL formats."""
    asin_match = re.search(r"/(?:dp|gp/product|exec/obidos/ASIN)/([A-Z0-9]{10})", url, re.IGNORECASE)
    if asin_match:
        return asin_match.group(1).upper()
    return ""


def attach_associate_tag(url: str, tag: str = "onyxdeals06-20") -> str:
    """
    Ensures the given Amazon URL contains the specified associate tag parameter.
    Cleans tracking noise and builds direct canonical Amazon affiliate URLs.
    """
    if not url:
        return url

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if "amazon" not in domain and "amzn" not in domain:
        return url

    # 1. Attempt clean ASIN extraction for standard Amazon product pages
    asin = extract_asin(url)
    if asin:
        clean_domain = "www.amazon.com" if "amzn" in domain else parsed.netloc
        return f"https://{clean_domain}/dp/{asin}?tag={tag}"

    # 2. Fallback for search/category Amazon URLs
    query_params = parse_qs(parsed.query)
    query_params["tag"] = [tag]
    
    # Remove clutter tracking params
    for unwanted_key in ["ref", "qid", "sr", "keywords_asin"]:
        query_params.pop(unwanted_key, None)

    new_query = urlencode(query_params, doseq=True)
    return urlunparse((
        parsed.scheme or "https",
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
