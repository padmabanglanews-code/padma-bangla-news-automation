"""Authenticated read-only HTTP adapter for local dashboard preview.

Binds to loopback only. No run/approve/publish/write endpoints are exposed.
For production, use a proper authenticated deployment and HTTPS reverse proxy.
"""
import hmac
import json
import os
from wsgiref.simple_server import make_server, WSGIServer

from .dashboard_readonly import build_dashboard_snapshot
from .persistent_dashboard import PersistentDashboardDraftStore


class DashboardReadOnlyApp:
    def __init__(self, *, token=None, store=None):
        self.token = token if token is not None else os.getenv("PADMA_DASHBOARD_TOKEN", "")
        self.store = store or PersistentDashboardDraftStore()

    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")
        supplied = environ.get("HTTP_AUTHORIZATION", "")
        expected = "Bearer " + self.token if self.token else ""
        if not self.token:
            return self._respond(start_response, "503 Service Unavailable",
                                 {"error": "dashboard_token_not_configured"})
        if not hmac.compare_digest(supplied, expected):
            return self._respond(start_response, "401 Unauthorized", {"error": "unauthorized"})
        if method != "GET":
            return self._respond(start_response, "405 Method Not Allowed",
                                 {"error": "read_only_endpoint"})
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
        start_response(status, [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("X-Content-Type-Options", "nosniff"),
        ])
        return [body]


def serve_local_dashboard(*, host="127.0.0.1", port=8765, token=None, store=None):
    """Serve the read-only API on loopback. Refuses non-loopback bind addresses."""
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("dashboard_server_loopback_only")
    app = DashboardReadOnlyApp(token=token, store=store)
    if not app.token:
        raise ValueError("PADMA_DASHBOARD_TOKEN is required")
    with make_server(host, int(port), app) as server:
        server.serve_forever()
