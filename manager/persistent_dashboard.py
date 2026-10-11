"""Persistent JSON-backed dashboard draft store; no HTTP server or external APIs.

This adapter is intended for a single-process prototype. It is not a substitute
for an authenticated database-backed production service.
"""
import json
import os
from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile

from .dashboard_api import DashboardAPIError, DashboardDraftStore
from .verification import verify_draft


class PersistentDashboardDraftStore:
    """Persist dashboard drafts atomically in a separate manager JSON file."""
    def __init__(self, path="manager/data/dashboard_drafts.json"):
        self.path = Path(path)

    def _read_items(self):
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DashboardAPIError("dashboard_store_unreadable_refusing_overwrite") from exc
        if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
            raise DashboardAPIError("dashboard_store_invalid_schema")
        seen = set()
        for item in data:
            draft_id = str(item.get("id", "")).strip()
            if not draft_id or draft_id in seen:
                raise DashboardAPIError("dashboard_store_invalid_or_duplicate_id")
            if item.get("review_status", "pending_review") not in {
                "pending_review", "approved_for_manual_next_step", "rejected"
            }:
                raise DashboardAPIError("dashboard_store_invalid_review_status")
            seen.add(draft_id)
        return data

    def _load_store(self):
        # Restore stored review status instead of resetting every draft to pending.
        store = DashboardDraftStore()
        for item in self._read_items():
            draft = deepcopy(item)
            draft_id = str(draft["id"])
            draft["review_status"] = str(draft.get("review_status", "pending_review"))
            draft["published"] = False
            draft["quality_report"] = verify_draft(draft)
            store._drafts[draft_id] = draft
        return store

    def _write_items(self, items):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent,
                                    delete=False) as handle:
                json.dump(items, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                temporary = Path(handle.name)
            os.replace(temporary, self.path)
        finally:
            if temporary and temporary.exists():
                temporary.unlink()

    def list_drafts(self):
        return self._load_store().list_drafts()

    def get_draft(self, draft_id):
        return self._load_store().get_draft(draft_id)

    def add_draft(self, draft, *, draft_id):
        store = self._load_store()
        result = store.add_draft(draft, draft_id=str(draft_id))
        self._write_items(store.list_drafts())
        return result

    def review_draft(self, draft_id, *, decision, reviewer_note=""):
        store = self._load_store()
        result = store.review_draft(draft_id, decision=decision, reviewer_note=reviewer_note)
        self._write_items(store.list_drafts())
        return result
