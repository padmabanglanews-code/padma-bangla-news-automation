"""Read-only local dashboard server with a same-origin UI and authenticated API.

Loopback only; no scheduler, RSS run, AI call, Blogger call, approval, or publishing.
"""
import hmac
import json
import os
from pathlib import Path
from wsgiref.simple_server import make_server

from .dashboard_readonly import build_dashboard_snapshot
from .persistent_dashboard import PersistentDashboardDraftStore

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "dashboard"
STATIC_ASSETS = {
    "/manager-live-adapter.js": ("manager-live-adapter.js", "application/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}


class DashboardReadOnlyApp:
    def __init__(self, *, token=None, store=None):
        self.token = token if token is not None else os.getenv("PADMA_DASHBOARD_TOKEN", "")
        self.store = store or PersistentDashboardDraftStore()

    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")
        if method != "GET":
            return self._respond(start_response, "405 Method Not Allowed",
                                 {"error": "read_only_endpoint"})

        # UI shell and fixed static assets are served from this same origin.
        if path in {"/", "/manager-live-adapter.html"}:
            try:
                body = (DASHBOARD_DIR / "manager-live-adapter.html").read_bytes()
            except OSError:
                return self._respond(start_response, "500 Internal Server Error",
                                     {"error": "dashboard_ui_unavailable"})
            return self._respond_bytes(start_response, "200 OK", body,
                                       "text/html; charset=utf-8")
        if path in STATIC_ASSETS:
            filename, content_type = STATIC_ASSETS[path]
            try:
                body = (DASHBOARD_DIR / filename).read_bytes()
            except OSError:
                return self._respond(start_response, "500 Internal Server Error",
                                     {"error": "dashboard_asset_unavailable"})
            return self._respond_bytes(start_response, "200 OK", body, content_type)

        supplied = environ.get("HTTP_AUTHORIZATION", "")
        expected = "Bearer " + self.token if self.token else ""
        if not self.token:
            return self._respond(start_response, "503 Service Unavailable",
                                 {"error": "dashboard_token_not_configured"})
        if not hmac.compare_digest(supplied, expected):
            return self._respond(start_response, "401 Unauthorized", {"error": "unauthorized"})
        try:
            if path == "/api/drafts":
                payload = {"drafts": self.store.list_drafts(), "published": False}
            elif path == "/api/dashboard":
                payload = build_dashboard_snapshot(
                    self.store.list_drafts(),
                    pipeline_status={"state": "read-only", "message": "কোনও live cycle এই API চালায় না।"},
                )
            elif path == "/health":
                payload = {"status": "ok", "read_only": True, "published": False}
            else:
                return self._respond(start_response, "404 Not Found", {"error": "not_found"})
        except (OSError, ValueError) as exc:
            return self._respond(start_response, "500 Internal Server Error",
                                 {"error": "dashboard_data_unavailable", "detail": str(exc)[:200]})
        return self._respond(start_response, "200 OK", payload)

    @staticmethod
    def _respond(start_response, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return DashboardReadOnlyApp._respond_bytes(
            start_response, status, body, "application/json; charset=utf-8"
        )

    @staticmethod
    def _respond_bytes(start_response, status, body, content_type):
        start_response(status, [
            ("Content-Type", content_type),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Security-Policy", "default-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"),
        ])
        return [body]


def serve_local_dashboard(*, host="127.0.0.1", port=8765, token=None, store=None):
    """Serve UI + read-only API on loopback. Requires a token and refuses public bind."""
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("dashboard_server_loopback_only")
    app = DashboardReadOnlyApp(token=token, store=store)
    if not app.token:
        raise ValueError("PADMA_DASHBOARD_TOKEN is required")
    with make_server(host, int(port), app) as server:
        server.serve_forever()
