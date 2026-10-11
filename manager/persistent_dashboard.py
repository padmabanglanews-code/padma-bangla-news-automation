"""Persistent JSON-backed dashboard draft store; no HTTP server or external APIs.

This adapter is intended for a single-process prototype. It is not a substitute
for an authenticated database-backed production service.
"""
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from .dashboard_api import DashboardAPIError, DashboardDraftStore


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
            seen.add(draft_id)
        return data

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
        return DashboardDraftStore(self._read_items()).list_drafts()

    def get_draft(self, draft_id):
        return DashboardDraftStore(self._read_items()).get_draft(draft_id)

    def add_draft(self, draft, *, draft_id):
        items = self._read_items()
        store = DashboardDraftStore(items)
        result = store.add_draft(draft, draft_id=str(draft_id))
        self._write_items(store.list_drafts())
        return result

    def review_draft(self, draft_id, *, decision, reviewer_note=""):
        items = self._read_items()
        store = DashboardDraftStore(items)
        result = store.review_draft(draft_id, decision=decision, reviewer_note=reviewer_note)
        self._write_items(store.list_drafts())
        return result
