"""Read-only dashboard view helpers; no HTTP server, network, or publishing."""
from copy import deepcopy
from .verification import verify_draft


def build_dashboard_snapshot(drafts=None, *, pipeline_status=None):
    """Build a JSON-serializable, read-only dashboard snapshot from supplied data."""
    items = []
    for index, raw in enumerate(drafts or []):
        if not isinstance(raw, dict):
            continue
        draft = deepcopy(raw)
        title = str(draft.get("title", "") or "").strip()
        source_url = str(draft.get("source_url", draft.get("link", "")) or "").strip()
        report = draft.get("quality_report")
        if not isinstance(report, dict):
            report = verify_draft(draft)
        items.append({
            "id": str(draft.get("id") or f"draft-{index + 1}"),
            "title": title or "(শিরোনাম নেই)",
            "summary": str(draft.get("summary", "") or ""),
            "source_url": source_url,
            "review_status": str(draft.get("review_status", "pending_review")),
            "quality_status": str(report.get("status", "needs_revision")),
            "quality_passed": bool(report.get("passed", False)),
            "quality_errors": list(report.get("errors", [])),
            "quality_warnings": list(report.get("warnings", [])),
            "published": False,
        })
    status = pipeline_status if isinstance(pipeline_status, dict) else {}
    return {
        "mode": "read-only-dashboard-snapshot",
        "draft_count": len(items),
        "pending_review_count": sum(1 for item in items if item["review_status"] == "pending_review"),
        "quality_passed_count": sum(1 for item in items if item["quality_passed"]),
        "drafts": items,
        "pipeline_status": {
            "state": str(status.get("state", "unknown")),
            "last_run": str(status.get("last_run", "")),
            "message": str(status.get("message", "")),
        },
        "read_only": True,
        "published": False,
    }
