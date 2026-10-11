import unittest
from manager.normalize import normalize_text,normalize_url
class NormalizeTests(unittest.TestCase):
 def test_tracking_removed(self): self.assertEqual(normalize_url("HTTPS://Example.com/a/?utm_source=x&lang=bn#top"),"https://example.com/a?lang=bn")
 def test_default_port_removed(self): self.assertEqual(normalize_url("https://example.com:443/a"),"https://example.com/a")
 def test_bad_url_safe(self): self.assertEqual(normalize_url("not a url"),"not a url")
 def test_text_whitespace(self): self.assertEqual(normalize_text("  NEWS   Update "),"news update")
if __name__=="__main__": unittest.main()
