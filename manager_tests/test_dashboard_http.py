import json
import unittest
from manager.dashboard_http import DashboardReadOnlyApp, serve_local_dashboard


class FakeStore:
    def list_drafts(self):
        return [{"id":"x","title":"নমুনা খবর","summary":"নমুনা সারাংশ",
                 "source_url":"https://example.org/news","published":True}]


def call(app, *, method="GET", path="/api/dashboard", authorization="Bearer test-secret"):
    captured = {}
    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)
    environ = {
        "REQUEST_METHOD": method, "PATH_INFO": path,
        "HTTP_AUTHORIZATION": authorization,
    }
    body = b"".join(app(environ, start_response))
    captured["body_bytes"] = body
    try:
        captured["body"] = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        captured["body"] = None
    return captured


class DashboardHttpTests(unittest.TestCase):
    def test_missing_token_fails_closed(self):
        result = call(DashboardReadOnlyApp(token=""), authorization="")
        self.assertEqual(result["status"], "503 Service Unavailable")

    def test_bad_token_rejected(self):
        result = call(DashboardReadOnlyApp(token="test-secret"), authorization="Bearer wrong")
        self.assertEqual(result["status"], "401 Unauthorized")

    def test_dashboard_endpoint_is_read_only_and_forces_unpublished(self):
        result = call(DashboardReadOnlyApp(token="test-secret", store=FakeStore()))
        self.assertEqual(result["status"], "200 OK")
        self.assertTrue(result["body"]["read_only"])
        self.assertFalse(result["body"]["published"])
        self.assertFalse(result["body"]["drafts"][0]["published"])

    def test_write_methods_rejected(self):
        result = call(DashboardReadOnlyApp(token="test-secret"), method="POST")
        self.assertEqual(result["status"], "405 Method Not Allowed")

    def test_unknown_route_not_found(self):
        result = call(DashboardReadOnlyApp(token="test-secret"), path="/api/publish")
        self.assertEqual(result["status"], "404 Not Found")

    def test_non_loopback_bind_rejected(self):
        with self.assertRaisesRegex(ValueError, "loopback_only"):
            serve_local_dashboard(host="0.0.0.0", token="test-secret")

    def test_ui_shell_is_served_same_origin_without_api_token(self):
        result = call(DashboardReadOnlyApp(token="test-secret"), path="/", authorization="")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn(b"manager-live-adapter.js", result["body_bytes"])
        self.assertIn("text/html", result["headers"]["Content-Type"])

    def test_fixed_javascript_asset_is_served_same_origin(self):
        result = call(DashboardReadOnlyApp(token="test-secret"), path="/manager-live-adapter.js", authorization="")
        self.assertEqual(result["status"], "200 OK")
        self.assertIn(b"/api/dashboard", result["body_bytes"])
        self.assertIn("javascript", result["headers"]["Content-Type"])


if __name__ == "__main__":
    unittest.main()
