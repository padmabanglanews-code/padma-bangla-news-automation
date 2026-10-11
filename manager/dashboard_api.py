"""Local dashboard service layer. No HTTP server, network calls, Blogger, or publishing."""
from copy import deepcopy
from .verification import verify_draft


class DashboardAPIError(ValueError):
    pass


class DashboardDraftStore:
    """In-memory draft registry intended for a future authenticated web adapter."""
    def __init__(self, drafts=None):
        self._drafts = {}
        for index, draft in enumerate(drafts or []):
            self.add_draft(draft, draft_id=str(draft.get("id") or f"draft-{index + 1}"))

    def add_draft(self, draft, *, draft_id):
        if not isinstance(draft, dict):
            raise DashboardAPIError("draft_must_be_object")
        if not draft_id or draft_id in self._drafts:
            raise DashboardAPIError("missing_or_duplicate_draft_id")
        item = deepcopy(draft)
        item["id"] = str(draft_id)
        item["review_status"] = "pending_review"
        item["published"] = False
        item["quality_report"] = verify_draft(item)
        self._drafts[str(draft_id)] = item
        return self.get_draft(str(draft_id))

    def list_drafts(self):
        return [self._public_view(item) for item in self._drafts.values()]

    def get_draft(self, draft_id):
        item = self._drafts.get(str(draft_id))
        if item is None:
            raise DashboardAPIError("draft_not_found")
        return self._public_view(item)

    def review_draft(self, draft_id, *, decision, reviewer_note=""):
        item = self._drafts.get(str(draft_id))
        if item is None:
            raise DashboardAPIError("draft_not_found")
        if decision not in {"approve", "reject"}:
            raise DashboardAPIError("decision_must_be_approve_or_reject")
        if item["review_status"] != "pending_review":
            raise DashboardAPIError("draft_already_reviewed")
        if decision == "approve" and not item["quality_report"]["passed"]:
            raise DashboardAPIError("quality_check_failed")
        item["review_status"] = "approved_for_manual_next_step" if decision == "approve" else "rejected"
        item["reviewer_note"] = str(reviewer_note)[:1000]
        # Approval is only an editorial decision; it never publishes or contacts Blogger.
        item["published"] = False
        return self._public_view(item)

    @staticmethod
    def _public_view(item):
        return deepcopy(item)
