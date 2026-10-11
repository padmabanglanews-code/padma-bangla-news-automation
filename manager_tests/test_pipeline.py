import unittest
from manager.pipeline import process_xml_feeds
class PipelineTests(unittest.TestCase):
 def test_dry_run_no_live_services(self):
  xml='<rss><channel><item><title>কলকাতার সরকারি খবর</title><link>https://example.com/a</link></item></channel></rss>'
  result=process_xml_feeds([{"xml":xml,"source":"demo"}]); self.assertEqual(result["mode"],"dry-run"); self.assertFalse(result["live_services_contacted"]); self.assertEqual(result["selected"],1)
 def test_bad_feed_and_good_feed(self):
  good='<rss><channel><item><title>India update</title><link>https://example.com/i</link></item></channel></rss>'
  result=process_xml_feeds([{"xml":"<rss>"},{"xml":good}]); self.assertEqual(len(result["feed_errors"]),1); self.assertEqual(result["selected"],1)
if __name__=="__main__": unittest.main()
