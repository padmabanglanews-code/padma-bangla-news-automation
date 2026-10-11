import unittest
from manager.dedupe import unique_stories
class DedupeTests(unittest.TestCase):
 def test_url_duplicate(self):
  rows,skipped=unique_stories([{"title":"A","link":"https://x.test/a?utm_source=x"},{"title":"B","link":"https://x.test/a"}]); self.assertEqual((len(rows),skipped),(1,1))
 def test_history_duplicate(self):
  rows,skipped=unique_stories([{"title":"A headline","link":"https://x.test/new"}],[{"title":"A headline","link":"https://x.test/old"}]); self.assertEqual((rows,skipped),([],1))
 def test_missing_fields_skipped(self): self.assertEqual(unique_stories([{"title":"No link"}]),([],1))
if __name__=="__main__": unittest.main()
