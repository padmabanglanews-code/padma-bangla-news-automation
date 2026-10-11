import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
_TRACKING_KEYS = {"fbclid", "gclid", "dclid", "mc_cid", "mc_eid", "ref", "ref_src"}
def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value or "")).strip().casefold()
def normalize_url(value: str) -> str:
    value = (value or "").strip()
    try:
        p = urlsplit(value)
        if p.scheme.lower() not in {"http", "https"} or not p.hostname: return value
        host = p.hostname.lower()
        if ":" in host and not host.startswith("["): host = f"[{host}]"
        port = p.port; netloc = host
        if port and not ((p.scheme.lower()=="http" and port==80) or (p.scheme.lower()=="https" and port==443)): netloc += f":{port}"
        query = [(k,v) for k,v in parse_qsl(p.query, keep_blank_values=True) if not (k.lower().startswith("utm_") or k.lower() in _TRACKING_KEYS)]
        return urlunsplit((p.scheme.lower(), netloc, p.path.rstrip("/") or "/", urlencode(query, doseq=True), ""))
    except (ValueError, UnicodeError): return value
