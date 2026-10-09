import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher

def normalize(text):
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text

def similarity(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

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
