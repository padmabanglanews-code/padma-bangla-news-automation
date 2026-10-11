"""Render WSGI entry point for the read-only dashboard only.

Requires Supabase-backed durable storage. Missing credentials fail closed rather
than silently falling back to Render's ephemeral filesystem.
No RSS collection, AI generation, Blogger writes, schedules, approvals, or
publishing are triggered by this entry point.
"""
import os

from .dashboard_http import DashboardReadOnlyApp
from .supabase_dashboard import SupabaseDashboardDraftStore

_token = os.getenv("PADMA_DASHBOARD_TOKEN", "")
if len(_token) < 24:
    raise RuntimeError(
        "PADMA_DASHBOARD_TOKEN must be set to a random secret of at least 24 characters"
    )

# Fail closed unless the durable store is configured. Never use ephemeral JSON
# storage as an implicit fallback on Render.
_store = SupabaseDashboardDraftStore()

# Render supplies PORT; Gunicorn binds externally. The exposed API remains GET-only.
app = DashboardReadOnlyApp(token=_token, store=_store)
