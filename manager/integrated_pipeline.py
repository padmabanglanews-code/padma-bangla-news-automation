"""Opt-in integration of RSS, OpenRouter drafts, QC and optional Blogger drafts.

All live effects require explicit flags. Publishing is not implemented.
"""
from .live_pipeline import collect_live_rss
from .draft_pipeline import generate_draft_candidates
from .verification import verify_draft_candidates
from .blogger_drafts import create_blogger_draft


def run_integrated_pipeline(*, live_rss=False, generate_ai=False, create_blogger_drafts=False,
                            sources_path="manager/feed_sources.json", rss_fetcher=None,
                            ai_generator=None, blogger_creator=None, history_store=None,
                            max_stories=5):
    """Run selected stages. Defaults to no network/API calls and no Blogger changes."""
    if create_blogger_drafts and not generate_ai:
        raise ValueError("create_blogger_drafts_requires_generate_ai")
    if generate_ai and not live_rss:
        raise ValueError("generate_ai_requires_live_rss")

    if not live_rss:
        return {
            "mode": "integration-safe-idle",
            "rss": {"stories": [], "published": False, "live_services_contacted": False},
            "ai_draft_candidates": [],
            "quality": {"reports": [], "passed_count": 0, "needs_revision_count": 0, "published": False},
            "blogger_results": [],
            "published": False,
            "blogger_contacted": False,
        }

    rss_kwargs = {
        "sources_path": sources_path,
        "history_store": history_store,
        "max_stories": max_stories,
    }
    if rss_fetcher is not None:
        rss_kwargs["fetcher"] = rss_fetcher
    rss_result = collect_live_rss(**rss_kwargs)

    candidates_result = {"candidates": [], "errors": [], "blogger_contacted": False, "published": False}
    if generate_ai:
        if ai_generator is None:
            candidates_result = generate_draft_candidates(rss_result.get("stories", []), limit=max_stories)
        else:
            candidates_result = generate_draft_candidates(
                rss_result.get("stories", []), generator=ai_generator, limit=max_stories
            )

    candidates = candidates_result["candidates"]
    quality = verify_draft_candidates(candidates)
    blogger_results = []
    blogger_contacted = False
    if create_blogger_drafts:
        creator = blogger_creator or create_blogger_draft
        for index, candidate in enumerate(candidates):
            report = quality["reports"][index]
            if not report["passed"]:
                blogger_results.append({
                    "status": "skipped_quality_failed",
                    "published": False,
                    "blogger_contacted": False,
                    "candidate_index": index,
                })
                continue
            try:
                result = creator(candidate)
                blogger_results.append({
                    "status": result.get("status", "unknown"),
                    "published": False,
                    "blogger_contacted": bool(result.get("blogger_contacted", True)),
                    "candidate_index": index,
                })
                blogger_contacted = blogger_contacted or bool(result.get("blogger_contacted", True))
            except (ValueError, OSError) as exc:
                blogger_results.append({
                    "status": "draft_creation_failed",
                    "error": str(exc),
                    "published": False,
                    "blogger_contacted": True,
                    "candidate_index": index,
                })
                blogger_contacted = True

    return {
        "mode": "integrated-draft-pipeline",
        "rss": rss_result,
        "ai_draft_candidates": candidates,
        "ai_errors": candidates_result["errors"],
        "quality": quality,
        "blogger_results": blogger_results,
        "blogger_contacted": blogger_contacted,
        "published": False,
    }
