import json
from pathlib import Path

QUEUE_FILE = Path("data/news_queue.json")

def load_queue():
    if not QUEUE_FILE.exists():
        return []
    return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))

def save_queue(items):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def add_story(story):
    queue = load_queue()

    links = {item.get("link") for item in queue}

    if story.get("link") in links:
        return False

    queue.append(story)
    save_queue(queue)
    return True

if __name__ == "__main__":
    print(json.dumps(load_queue(), ensure_ascii=False, indent=2))
