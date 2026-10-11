"""Separate atomic history storage; never touches data/news_queue.json."""
import json, os
from pathlib import Path
from tempfile import NamedTemporaryFile
class HistoryStore:
    def __init__(self,path="manager/data/history.json"): self.path=Path(path)
    def load(self):
        if not self.path.exists(): return []
        try: data=json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError) as exc: raise ValueError("Manager history is unreadable; refusing to overwrite it") from exc
        if not isinstance(data,list) or any(not isinstance(x,dict) for x in data): raise ValueError("Manager history must be a JSON array of objects")
        return data
    def save(self,items):
        self.path.parent.mkdir(parents=True,exist_ok=True); tmp=None
        try:
            with NamedTemporaryFile("w",encoding="utf-8",dir=self.path.parent,delete=False) as f:
                json.dump(items,f,ensure_ascii=False,indent=2); f.write("\n"); tmp=Path(f.name)
            os.replace(tmp,self.path)
        finally:
            if tmp and tmp.exists(): tmp.unlink()
