from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DashboardAdapterStaticTests(unittest.TestCase):
    def test_adapter_html_loads_expected_assets(self):
        html = (ROOT / "dashboard" / "manager-live-adapter.html").read_text(encoding="utf-8")
        self.assertIn('id="padma-live-dash"', html)
        self.assertIn('href="style.css"', html)
        self.assertIn('src="manager-live-adapter.js"', html)

    def test_adapter_only_requests_read_only_dashboard_endpoint(self):
        js = (ROOT / "dashboard" / "manager-live-adapter.js").read_text(encoding="utf-8")
        self.assertIn("fetch('/api/dashboard'", js)
        self.assertIn("method: 'GET'", js)
        self.assertNotIn("localStorage", js)
        self.assertNotIn("sessionStorage", js)
        self.assertNotIn("innerHTML", js)

    def test_adapter_has_disconnect_and_no_publish_controls(self):
        js = (ROOT / "dashboard" / "manager-live-adapter.js").read_text(encoding="utf-8")
        self.assertIn("function disconnect()", js)
        self.assertIn("token = ''", js)
        self.assertNotIn("POST", js)
        self.assertNotIn("/api/publish", js)
        self.assertNotIn("/api/run", js)
        self.assertNotIn("/api/approve", js)


if __name__ == "__main__":
    unittest.main()
