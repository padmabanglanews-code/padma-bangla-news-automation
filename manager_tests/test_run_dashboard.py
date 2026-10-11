import os
import unittest
from unittest.mock import patch
from manager import run_dashboard


class DashboardRunnerTests(unittest.TestCase):
    def test_short_or_missing_token_fails_before_server_start(self):
        with patch.dict(os.environ, {"PADMA_DASHBOARD_TOKEN": "short"}, clear=False):
            with self.assertRaisesRegex(SystemExit, "at least 24 characters"):
                run_dashboard.main()

    def test_valid_token_starts_loopback_server_only(self):
        with patch.dict(os.environ, {"PADMA_DASHBOARD_TOKEN": "x" * 32}, clear=False), \
             patch("manager.run_dashboard.serve_local_dashboard") as serve:
            run_dashboard.main()
            serve.assert_called_once_with(host="127.0.0.1", port=8765, token="x" * 32)


if __name__ == "__main__":
    unittest.main()
