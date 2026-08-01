from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def attach_associate_tag(url: str, tag: str = "onyxdeals06-20") -> str:
    """
    Ensures the given Amazon URL contains the specified associate tag parameter.
    """
    if not url:
        return url

    parsed = urlparse(url)
    
    # Verify domain is Amazon-related
    if "amazon" not in parsed.netloc.lower() and "amzn" not in parsed.netloc.lower():
        return url

    query_params = parse_qs(parsed.query)
    query_params["tag"] = [tag]
    
    # Reconstruct query string and URL
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    return new_url
