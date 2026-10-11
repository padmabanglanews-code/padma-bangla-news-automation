"""Controlled RSS fetching for explicit, manually invoked runs only.

This module is never called by the existing scheduled workflow or by pipeline.py.
It accepts HTTPS feed URLs, applies strict time/size limits, and re-checks redirects.
"""
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import ipaddress
import socket

USER_AGENT = "PadmaBanglaNewsManager/0.1 (RSS reader)"
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_MAX_BYTES = 1_000_000


def _validate_public_https_url(url: str) -> None:
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() != "https" or not parsed.hostname:
            raise ValueError("Feed URL must use HTTPS")
        if parsed.username or parsed.password:
            raise ValueError("Feed URL must not contain credentials")
        host = parsed.hostname.rstrip(".").lower()
        if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
            raise ValueError("Local feed hosts are not allowed")
        try:
            addresses = {ipaddress.ip_address(host)}
        except ValueError:
            try:
                addresses = {ipaddress.ip_address(info[4][0]) for info in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
            except OSError as exc:
                raise ValueError("Could not resolve feed host") from exc
        if not addresses or any(not addr.is_global for addr in addresses):
            raise ValueError("Feed host must resolve only to public IP addresses")
    except (TypeError, AttributeError) as exc:
        raise ValueError("Invalid feed URL") from exc


def fetch_feed_xml(url: str, *, timeout: int = DEFAULT_TIMEOUT_SECONDS,
                   max_bytes: int = DEFAULT_MAX_BYTES) -> str:
    """Fetch one HTTPS RSS/Atom document. This function is opt-in, not automatic."""
    _validate_public_https_url(url)
    if not 1 <= timeout <= 30:
        raise ValueError("timeout must be between 1 and 30 seconds")
    if not 1 <= max_bytes <= 2_000_000:
        raise ValueError("max_bytes must be between 1 and 2000000")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"})
    try:
        with urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
            _validate_public_https_url(final_url)
            content_type = response.headers.get("Content-Type", "").lower()
            if content_type and not any(kind in content_type for kind in ("xml", "rss", "atom", "text/plain", "octet-stream")):
                raise ValueError("Feed response did not look like XML")
            data = response.read(max_bytes + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise ValueError("RSS feed request failed") from exc
    if len(data) > max_bytes:
        raise ValueError("RSS feed exceeded the maximum response size")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("RSS feed was not valid UTF-8") from exc
