"""Dashboard orchestration facade. No scheduler or HTTP server is started here."""
from .integrated_pipeline import run_integrated_pipeline
from .persistent_dashboard import PersistentDashboardDraftStore
from .dashboard_readonly import build_dashboard_snapshot


def run_dashboard_cycle(*, live_rss=False, generate_ai=False, create_blogger_drafts=False,
                        sources_path="manager/feed_sources.json", rss_fetcher=None,
                        ai_generator=None, blogger_creator=None, history_store=None,
                        max_stories=5, store=None):
    """Run one explicitly selected cycle and persist generated candidates for review.

    Defaults are safe-idle. Live RSS, AI calls and Blogger draft creation each need
    explicit opt-in flags. No publish functionality exists.
    """
    pipeline = run_integrated_pipeline(
        live_rss=live_rss,
        generate_ai=generate_ai,
        create_blogger_drafts=create_blogger_drafts,
        sources_path=sources_path,
        rss_fetcher=rss_fetcher,
        ai_generator=ai_generator,
        blogger_creator=blogger_creator,
        history_store=history_store,
        max_stories=max_stories,
    )
    draft_store = store or PersistentDashboardDraftStore()
    saved_ids = []
    for index, candidate in enumerate(pipeline.get("ai_draft_candidates", [])):
        source_url = str(candidate.get("source_url", candidate.get("link", "")) or "")
        draft_id = "news-" + str(abs(hash((source_url, candidate.get("title", "")))))
        try:
            draft_store.add_draft(candidate, draft_id=draft_id)
            saved_ids.append(draft_id)
        except ValueError as exc:
            # Do not overwrite an existing draft: stable IDs provide basic deduplication.
            if "duplicate" in str(exc):
                saved_ids.append(draft_id)
            else:
                raise
    snapshot = build_dashboard_snapshot(
        draft_store.list_drafts(),
        pipeline_status={
            "state": pipeline.get("mode", "unknown"),
            "message": "Publish বন্ধ; AI-generated লেখা মানব-সম্পাদককে যাচাই করতে হবে।",
        },
    )
    return {
        "mode": "dashboard-cycle",
        "pipeline": pipeline,
        "saved_draft_ids": saved_ids,
        "dashboard": snapshot,
        "published": False,
    }
