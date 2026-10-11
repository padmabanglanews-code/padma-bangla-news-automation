"""Opt-in live RSS collection with dry-run-only processing; never publishes."""
import json
from pathlib import Path
from .live_rss import fetch_feed_xml
from .pipeline import process_xml_feeds


def load_feed_sources(path="manager/feed_sources.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    feeds = data.get("feeds")
    if not isinstance(feeds, list):
        raise ValueError("Feed source configuration must contain a feeds array")
    for feed in feeds:
        if not isinstance(feed, dict) or not all(feed.get(key) for key in ("id", "name", "url", "region", "category")):
            raise ValueError("Each feed must define id, name, url, region, and category")
        if not isinstance(feed.get("enabled", False), bool):
            raise ValueError("Feed enabled flag must be boolean")
    return [feed for feed in feeds if feed.get("enabled", False)]


def collect_live_rss(*, sources_path="manager/feed_sources.json", history_store=None,
                     max_stories=20, fetcher=fetch_feed_xml):
    """Fetch enabled public feeds, parse/rank stories, and return a dry-run result."""
    feed_inputs = []
    fetch_errors = []
    for source in load_feed_sources(sources_path):
        try:
            xml = fetcher(source["url"])
            feed_inputs.append({"xml": xml, "source": source["name"], "category": source["category"]})
        except (ValueError, OSError) as exc:
            fetch_errors.append({"source": source["name"], "error": str(exc)})
    result = process_xml_feeds(feed_inputs, history_store=history_store, max_stories=max_stories)
    result["mode"] = "live-rss-dry-run"
    result["feeds_configured"] = len(load_feed_sources(sources_path))
    result["feeds_fetched"] = len(feed_inputs)
    result["fetch_errors"] = fetch_errors
    result["live_services_contacted"] = bool(feed_inputs)
    result["published"] = False
    return result
