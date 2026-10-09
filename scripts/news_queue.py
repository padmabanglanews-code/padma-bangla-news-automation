import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from datetime import datetime
from zoneinfo import ZoneInfo

QUEUE_FILE = Path(os.getenv("NEWS_QUEUE_FILE", "data/news_queue.json"))

def load_queue():
    if not QUEUE_FILE.exists():
        return []
    items = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise ValueError("News queue must contain a JSON array")
    return items

def save_queue(items):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=QUEUE_FILE.parent, delete=False) as temporary:
        json.dump(items, temporary, ensure_ascii=False, indent=2)
        temporary.write("\n")
        temporary_path = Path(temporary.name)
    temporary_path.replace(QUEUE_FILE)

def add_story(story):
    queue = load_queue()

    links = {item.get("link") for item in queue}

    if story.get("link") in links:
        return False

    queue.append(story)
    save_queue(queue)
    return True

def published_today(items, today=None):
    today = today or datetime.now(ZoneInfo("Asia/Kolkata")).date()
    count = 0
    for item in items:
        published_at = item.get("blogger_published_at")
        if not published_at:
            continue
        try:
            published_date = datetime.fromisoformat(published_at).astimezone(
                ZoneInfo("Asia/Kolkata")
            ).date()
        except (TypeError, ValueError):
            continue
        if published_date == today:
            count += 1
    return count

if __name__ == "__main__":
    print(json.dumps(load_queue(), ensure_ascii=False, indent=2))