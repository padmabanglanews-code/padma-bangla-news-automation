import json
import tempfile
import unittest
from pathlib import Path
from manager.end_to_end import run_end_to_end


class EndToEndTests(unittest.TestCase):
    def test_mock_end_to_end_does_not_contact_blogger_or_publish(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "feeds.json"
            path.write_text(json.dumps({"feeds": [{
                "id":"demo","name":"Demo","url":"https://example.org/rss",
                "region":"west_bengal","category":"local","enabled":True
            }]}), encoding="utf-8")
            xml = '<rss><channel><item><title>কলকাতার খবর</title><link>https://example.org/a</link><description>পরীক্ষার বিবরণ</description></item></channel></rss>'
            def fake_ai(story):
                return {"title":"খসড়া: "+story["title"],"body":"পরীক্ষার খসড়া","summary":"সারাংশ","status":"draft_candidate","published":False}
            result = run_end_to_end(sources_path=path, rss_fetcher=lambda url: xml, ai_generator=fake_ai)
            self.assertEqual(result["mode"], "end-to-end-dry-run")
            self.assertEqual(len(result["ai_draft_candidates"]), 1)
            self.assertFalse(result["blogger_draft_created"])
            self.assertFalse(result["blogger_contacted"])
            self.assertFalse(result["published"])

    def test_ai_failure_does_not_trigger_blogger(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "feeds.json"
            path.write_text(json.dumps({"feeds": [{
                "id":"demo","name":"Demo","url":"https://example.org/rss",
                "region":"west_bengal","category":"local","enabled":True
            }]}), encoding="utf-8")
            xml = '<rss><channel><item><title>কলকাতার খবর</title><link>https://example.org/a</link></item></channel></rss>'
            def fail_ai(story): raise ValueError("mock AI error")
            result = run_end_to_end(sources_path=path, rss_fetcher=lambda url: xml, ai_generator=fail_ai)
            self.assertEqual(len(result["ai_errors"]), 1)
            self.assertFalse(result["blogger_contacted"])
            self.assertFalse(result["published"])


if __name__ == "__main__": unittest.main()
