"""Explicit opt-in OpenRouter draft generation; no Blogger or publishing calls."""
from .openrouter_client import generate_bengali_draft


def generate_draft_candidates(stories, *, generator=generate_bengali_draft, limit=5):
    candidates = []
    errors = []
    for story in list(stories)[:max(0, limit)]:
        try:
            candidates.append(generator(story))
        except ValueError as exc:
            errors.append({"source_url": str(story.get("link", "")), "error": str(exc)})
    return {
        "mode": "ai-draft-candidates",
        "candidates": candidates,
        "errors": errors,
        "published": False,
        "blogger_contacted": False
    }
