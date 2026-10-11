"""End-to-end orchestration. Defaults to mocks/dry-run; publishing is never automatic."""
from .live_pipeline import collect_live_rss
from .draft_pipeline import generate_draft_candidates


def run_end_to_end(*, sources_path="manager/feed_sources.json", rss_fetcher=None,
                   ai_generator=None, history_store=None, max_stories=5):
    """Collect feeds, rank stories, and create AI draft candidates. Never calls Blogger."""
    rss_kwargs = {"sources_path": sources_path, "history_store": history_store, "max_stories": max_stories}
    if rss_fetcher is not None:
        rss_kwargs["fetcher"] = rss_fetcher
    rss_result = collect_live_rss(**rss_kwargs)
    generator = ai_generator
    if generator is None:
        candidates_result = generate_draft_candidates(rss_result["stories"], limit=max_stories)
    else:
        candidates_result = generate_draft_candidates(rss_result["stories"], generator=generator, limit=max_stories)
    return {
        "mode": "end-to-end-dry-run",
        "rss": rss_result,
        "ai_draft_candidates": candidates_result["candidates"],
        "ai_errors": candidates_result["errors"],
        "blogger_draft_created": False,
        "blogger_contacted": False,
        "published": False
    }
