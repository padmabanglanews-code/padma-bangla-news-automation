"""Deterministic editorial quality checks for AI draft candidates; no network or publishing."""
import re
from urllib.parse import urlsplit


def verify_draft(draft):
    """Return a QC report. This checks structure/quality signals, not factual truth."""
    if not isinstance(draft, dict):
        draft = {}
    title = str(draft.get("title", "") or "").strip()
    body = str(draft.get("body", "") or "").strip()
    summary = str(draft.get("summary", "") or "").strip()
    source_url = str(draft.get("source_url", draft.get("link", "")) or "").strip()
    errors = []
    warnings = []

    if len(title) < 8:
        errors.append("title_too_short")
    if len(title) > 180:
        warnings.append("title_too_long")
    if len(body) < 120:
        errors.append("body_too_short")
    if len(body) > 20000:
        warnings.append("body_very_long")
    if len(summary) < 20:
        errors.append("summary_too_short")
    if len(summary) > 400:
        warnings.append("summary_too_long")
    if not source_url:
        errors.append("missing_source_url")
    else:
        try:
            parsed = urlsplit(source_url)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                errors.append("invalid_source_url")
        except ValueError:
            errors.append("invalid_source_url")

    normalized_title = re.sub(r"[^\w\u0980-\u09FF]+", "", title.casefold())
    normalized_body = re.sub(r"[^\w\u0980-\u09FF]+", "", body.casefold())
    if normalized_title and normalized_title in normalized_body:
        warnings.append("title_repeated_in_body")
    searchable_text = (title + " " + body + " " + summary).casefold()

    # Bengali news drafts must not silently mix Devanagari or other scripts.
    # Allow Latin characters for names/acronyms/URLs, but reject Devanagari
    # and common non-Bengali Indic scripts as a conservative editorial gate.
    devanagari = re.compile(r"[\u0900-\u097F]")
    if devanagari.search(title + " " + body + " " + summary):
        errors.append("non_bengali_devanagari_script")
    if not re.search(r"[\u0980-\u09FF]", title + " " + body):
        errors.append("bengali_script_missing")

    placeholders = (
        "lorem ipsum",
        "as an ai language model",
        "insert headline",
        "placeholder text",
    )
    if any(phrase in searchable_text for phrase in placeholders):
        errors.append("placeholder_or_ai_meta_text")
    if not draft.get("verification_notes"):
        warnings.append("human_fact_check_required")

    passed = not errors
    return {
        "passed": passed,
        "status": "ready_for_editor_review" if passed else "needs_revision",
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "title_chars": len(title),
            "body_chars": len(body),
            "summary_chars": len(summary),
            "source_url_present": bool(source_url),
            "factual_accuracy_verified": False,
        },
        "published": False,
    }


def verify_draft_candidates(candidates):
    """Verify candidates without changing them or contacting external services."""
    reports = []
    for index, candidate in enumerate(candidates or []):
        report = verify_draft(candidate)
        report["candidate_index"] = index
        reports.append(report)
    return {
        "mode": "editorial-qc-offline",
        "reports": reports,
        "passed_count": sum(1 for item in reports if item["passed"]),
        "needs_revision_count": sum(1 for item in reports if not item["passed"]),
        "published": False,
    }
