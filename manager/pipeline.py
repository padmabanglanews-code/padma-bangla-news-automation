"""Dry-run pipeline foundation: supplied XML only, no network or API calls."""
from .dedupe import unique_stories
from .ranking import rank_stories
from .rss_collector import parse_feed

def process_xml_feeds(feeds: list[dict], *, history_store=None, max_stories: int=20) -> dict:
    collected=[]; errors=[]
    for feed in feeds:
        try: collected.extend(parse_feed(feed.get("xml",""),source=feed.get("source",""),category=feed.get("category","general")))
        except ValueError as exc: errors.append({"source":str(feed.get("source","")),"error":str(exc)})
    history=history_store.load() if history_store else []
    unique,skipped=unique_stories(collected,history); ranked=rank_stories(unique)[:max(0,max_stories)]
    return {"mode":"dry-run","collected":len(collected),"duplicates_skipped":skipped,"selected":len(ranked),"stories":ranked,"feed_errors":errors,"history_count":len(history),"live_services_contacted":False}
