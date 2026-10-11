import unittest
from manager.rss_collector import parse_feed
class RSSParserTests(unittest.TestCase):
 def test_rss_item(self):
  rows=parse_feed('<rss><channel><item><title>কলকাতার খবর</title><link>https://example.com/a</link><description>বিবরণ</description></item></channel></rss>',source="Demo")
  self.assertEqual(len(rows),1); self.assertEqual(rows[0]["source"],"Demo")
 def test_atom_entry(self):
  xml='<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>India update</title><link href="https://example.com/i"/><summary>Update</summary></entry></feed>'
  self.assertEqual(parse_feed(xml)[0]["link"],"https://example.com/i")
 def test_malformed(self):
  with self.assertRaises(ValueError): parse_feed("<rss>")
 def test_missing_fields_skipped(self): self.assertEqual(parse_feed("<rss><channel><item><title>Missing link</title></item></channel></rss>"),[])
if __name__=="__main__": unittest.main()
