"""Supabase-backed draft storage for the hosted dashboard.

Only instantiate this adapter on the server. Keep SUPABASE_URL and
SUPABASE_SECRET_KEY in the hosting provider's secret environment.
SUPABASE_SERVICE_ROLE_KEY remains a backwards-compatible legacy fallback.
This module does not create tables, call news APIs, or publish content.
"""
import os
from copy import deepcopy

from .dashboard_api import DashboardAPIError, DashboardDraftStore
from .verification import verify_draft

_ALLOWED_STATUSES = {
    "pending_review", "approved_for_manual_next_step", "rejected"
}


class SupabaseDashboardDraftStore:
    """Persist dashboard drafts/review metadata in a pre-created Supabase table."""

    def __init__(self, *, client=None, table_name="dashboard_drafts"):
        if client is None:
            url = os.getenv("SUPABASE_URL", "").strip()
            # Supabase's current sb_secret_* key is preferred; the old
            # JWT-based service_role key remains supported during migration.
            key = (
                os.getenv("SUPABASE_SECRET_KEY", "").strip()
                or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
            )
            if not url or not key:
                raise RuntimeError(
                    "SUPABASE_URL and SUPABASE_SECRET_KEY are required"
                )
            try:
                from supabase import create_client
            except ImportError as exc:
                raise RuntimeError(
                    "Install the supabase package to use hosted dashboard storage"
                ) from exc
            client = create_client(url, key)
        self.client = client
        self.table_name = table_name

    def _table(self):
        return self.client.table(self.table_name)

    @staticmethod
    def _row_to_draft(row):
        if not isinstance(row, dict) or not isinstance(row.get("draft"), dict):
            raise DashboardAPIError("supabase_dashboard_invalid_row")
        draft = deepcopy(row["draft"])
        draft_id = str(row.get("id", "")).strip()
        status = row.get("review_status", "pending_review")
        if not draft_id or status not in _ALLOWED_STATUSES:
            raise DashboardAPIError("supabase_dashboard_invalid_id_or_status")
        draft["id"] = draft_id
        draft["review_status"] = status
        draft["reviewer_note"] = str(row.get("reviewer_note") or "")[:1000]
        draft["published"] = False
        draft["quality_report"] = verify_draft(draft)
        return draft

    def list_drafts(self):
        response = self._table().select("*").order("created_at").execute()
        rows = getattr(response, "data", None)
        if not isinstance(rows, list):
            raise DashboardAPIError("supabase_dashboard_invalid_response")
        return [self._row_to_draft(row) for row in rows]

    def get_draft(self, draft_id):
        response = self._table().select("*").eq("id", str(draft_id)).limit(1).execute()
        rows = getattr(response, "data", None)
        if not isinstance(rows, list) or not rows:
            raise DashboardAPIError("draft_not_found")
        return self._row_to_draft(rows[0])

    def add_draft(self, draft, *, draft_id):
        validator = DashboardDraftStore()
        item = validator.add_draft(draft, draft_id=str(draft_id))
        row = {
            "id": str(draft_id),
            "draft": {k: deepcopy(v) for k, v in item.items()
                      if k not in {"id", "review_status", "reviewer_note",
                                   "quality_report", "published"}},
            "review_status": "pending_review",
            "reviewer_note": "",
            "published": False,
        }
        self._table().insert(row).execute()
        return self.get_draft(str(draft_id))

    def review_draft(self, draft_id, *, decision, reviewer_note=""):
        current = self.get_draft(draft_id)
        validator = DashboardDraftStore([current])
        validated_id = str(current["id"])
        validator._drafts[validated_id]["review_status"] = current["review_status"]
        result = validator.review_draft(
            validated_id, decision=decision, reviewer_note=reviewer_note
        )
        self._table().update({
            "review_status": result["review_status"],
            "reviewer_note": str(reviewer_note)[:1000],
            "published": False,
        }).eq("id", validated_id).execute()
        return self.get_draft(validated_id)
