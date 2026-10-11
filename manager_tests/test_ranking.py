import unittest
from manager.ranking import rank_stories
class RankingTests(unittest.TestCase):
 def test_west_bengal_first(self):
  rows=rank_stories([{"title":"International summit","link":"https://x/i"},{"title":"কলকাতায় সরকারি ঘোষণা","link":"https://x/w"}]); self.assertEqual(rows[0]["region"],"west_bengal")
 def test_india_above_international(self):
  rows=rank_stories([{"title":"World summit","link":"https://x/w"},{"title":"India budget","link":"https://x/i"}]); self.assertEqual(rows[0]["region"],"india")
if __name__=="__main__": unittest.main()
