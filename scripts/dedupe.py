import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from urllib.parse import urlsplit, urlunsplit

def normalize(text):
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text

def similarity(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def canonical_link(link):
    parts = urlsplit(link or "")
    if not parts.scheme or not parts.netloc:
        return (link or "").strip()
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))

def is_duplicate(story, existing):
    story_link = canonical_link(story.get("link"))
    story_title = story.get("title", "")

    for item in existing:
        if story_link and story_link == canonical_link(item.get("link")):
            return True
        previous_titles = [item.get("title", "")]
        article = item.get("article", {})
        if isinstance(article, dict):
            previous_titles.append(article.get("headline", ""))
        if story_title and any(similarity(story_title, title) >= 0.82 for title in previous_titles):
            return True
    return False

def main():
    data = json.load(sys.stdin)

    seen = []
    output = []

    for story in data:
        title = story.get("title", "")
        if not title:
            continue

        duplicate = any(similarity(title, old) >= 0.82 for old in seen)

        if not duplicate:
            output.append(story)
            seen.append(title)

    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
