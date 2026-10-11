import tempfile,unittest
from pathlib import Path
from manager.queue import HistoryStore
class HistoryTests(unittest.TestCase):
 def test_atomic_store_roundtrip(self):
  with tempfile.TemporaryDirectory() as d:
   store=HistoryStore(Path(d)/"history.json"); store.save([{"title":"খবর"}]); self.assertEqual(store.load(),[{"title":"খবর"}])
 def test_corrupt_file_refuses_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"history.json"; path.write_text("{",encoding="utf-8")
   with self.assertRaises(ValueError): HistoryStore(path).load()
if __name__=="__main__": unittest.main()
