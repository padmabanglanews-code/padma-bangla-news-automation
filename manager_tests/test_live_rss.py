import unittest
from unittest.mock import patch
from manager.live_rss import _validate_public_https_url, fetch_feed_xml


class FakeHeaders(dict):
    pass


class FakeResponse:
    def __init__(self, data, url="https://feeds.example.org/rss", content_type="application/rss+xml"):
        self.data = data
        self.headers = FakeHeaders({"Content-Type": content_type})
        self.url = url
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def geturl(self): return self.url
    def read(self, size=-1): return self.data[:size]


class LiveRSSGuardTests(unittest.TestCase):
    def test_rejects_http(self):
        with self.assertRaises(ValueError):
            _validate_public_https_url("http://example.org/rss")

    def test_rejects_local_host(self):
        with self.assertRaises(ValueError):
            _validate_public_https_url("https://localhost/rss")

    @patch("manager.live_rss._validate_public_https_url")
    @patch("manager.live_rss.urlopen")
    def test_fetch_uses_limits_and_returns_xml(self, mock_open, mock_validate):
        mock_open.return_value = FakeResponse(b"<rss/>")
        self.assertEqual(fetch_feed_xml("https://feeds.example.org/rss"), "<rss/>")
        mock_open.assert_called_once()
        self.assertEqual(mock_validate.call_count, 2)

    @patch("manager.live_rss._validate_public_https_url")
    @patch("manager.live_rss.urlopen")
    def test_rejects_oversized_response(self, mock_open, mock_validate):
        mock_open.return_value = FakeResponse(b"12345")
        with self.assertRaises(ValueError):
            fetch_feed_xml("https://feeds.example.org/rss", max_bytes=4)


if __name__ == "__main__":
    unittest.main()
