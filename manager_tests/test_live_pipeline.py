import json
import tempfile
import unittest
from pathlib import Path
from manager.live_pipeline import collect_live_rss, load_feed_sources


class LivePipelineTests(unittest.TestCase):
    def test_collects_mock_feed_and_does_not_publish(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "feeds.json"
            path.write_text(json.dumps({"feeds": [{
                "id": "demo", "name": "Demo", "url": "https://example.org/rss",
                "region": "west_bengal", "category": "local", "enabled": True
            }]}), encoding="utf-8")
            xml = '<rss><channel><item><title>কলকাতার খবর</title><link>https://example.org/a</link></item></channel></rss>'
            result = collect_live_rss(sources_path=path, fetcher=lambda url: xml)
            self.assertEqual(result["mode"], "live-rss-dry-run")
            self.assertEqual(result["feeds_fetched"], 1)
            self.assertEqual(result["selected"], 1)
            self.assertFalse(result["published"])

    def test_fetch_error_does_not_stop_other_feeds(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "feeds.json"
            path.write_text(json.dumps({"feeds": [
                {"id":"bad","name":"Bad","url":"https://bad.example/rss","region":"india","category":"national","enabled":True},
                {"id":"good","name":"Good","url":"https://good.example/rss","region":"india","category":"national","enabled":True}
            ]}), encoding="utf-8")
            xml = '<rss><channel><item><title>India news</title><link>https://good.example/a</link></item></channel></rss>'
            def fake(url):
                if "bad.example" in url: raise ValueError("mock failure")
                return xml
            result = collect_live_rss(sources_path=path, fetcher=fake)
            self.assertEqual(result["feeds_fetched"], 1)
            self.assertEqual(len(result["fetch_errors"]), 1)
            self.assertEqual(result["selected"], 1)

    def test_invalid_feed_config_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "feeds.json"
            path.write_text('{"feeds":[{"name":"missing required fields"}]}', encoding="utf-8")
            with self.assertRaises(ValueError): load_feed_sources(path)


if __name__ == "__main__": unittest.main()
