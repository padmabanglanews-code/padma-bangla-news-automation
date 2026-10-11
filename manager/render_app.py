"""Render WSGI entry point for the read-only dashboard only.

This module never runs RSS collection, AI generation, Blogger writes, schedules,
approvals, or publishing. Configure PADMA_DASHBOARD_TOKEN in the host environment.
"""
import os

from .dashboard_http import DashboardReadOnlyApp

_token = os.getenv("PADMA_DASHBOARD_TOKEN", "")
if len(_token) < 24:
    raise RuntimeError("PADMA_DASHBOARD_TOKEN must be set to a random secret of at least 24 characters")

# Render supplies PORT; Gunicorn binds externally, while the existing local runner
# remains loopback-only. The app itself exposes only the existing read-only routes.
app = DashboardReadOnlyApp(token=_token)
