"""Blogger API draft-only client. No publish method is exposed."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

BLOGGER_API = "https://www.googleapis.com/blogger/v3/blogs"


def create_blogger_draft(draft: dict, *, access_token=None, blog_id=None, timeout=20, opener=urlopen):
    """Create a Blogger draft only. The API is called only when this function is explicitly invoked."""
    token = access_token or os.getenv("BLOGGER_ACCESS_TOKEN")
    blog = blog_id or os.getenv("BLOGGER_BLOG_ID")
    if not token:
        raise ValueError("BLOGGER_ACCESS_TOKEN is not configured")
    if not blog:
        raise ValueError("BLOGGER_BLOG_ID is not configured")
    if not isinstance(draft, dict):
        raise ValueError("Draft must be an object")
    title = str(draft.get("title", "")).strip()
    content = str(draft.get("body", "")).strip()
    if not title or not content:
        raise ValueError("Draft must contain title and body")
    if not 1 <= timeout <= 60:
        raise ValueError("timeout must be between 1 and 60 seconds")

    # isDraft=true is always forced here; callers cannot override it.
    url = f"{BLOGGER_API}/{quote(str(blog), safe='')}/posts?isDraft=true"
    payload = json.dumps({"kind":"blogger#post", "title":title[:300], "content":content}).encode("utf-8")
    request = Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read(1_000_001)
    except HTTPError as exc:
        raise ValueError(f"Blogger draft request failed with HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ValueError("Blogger draft request failed") from exc
    if len(raw) > 1_000_000:
        raise ValueError("Blogger response exceeded size limit")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Blogger returned invalid JSON") from exc
    if not isinstance(result, dict) or not result.get("id"):
        raise ValueError("Blogger response did not confirm draft creation")
    return {
        "status": "draft_created",
        "published": False,
        "id": str(result["id"]),
        "title": str(result.get("title", title)),
        "url": str(result.get("url", "")),
        "blogger_contacted": True
    }
