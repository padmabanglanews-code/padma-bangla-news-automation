from difflib import SequenceMatcher
from .normalize import normalize_text, normalize_url
def is_duplicate(story: dict, existing: list[dict], threshold: float=0.88) -> bool:
    link=normalize_url(str(story.get("link",""))); title=normalize_text(str(story.get("title","")))
    for old in existing:
        old_link=normalize_url(str(old.get("link","")))
        if link and old_link and link==old_link: return True
        old_title=normalize_text(str(old.get("title","")))
        if title and old_title and SequenceMatcher(None,title,old_title).ratio()>=threshold: return True
    return False
def unique_stories(stories: list[dict], history: list[dict] | None=None) -> tuple[list[dict],int]:
    seen=list(history or []); accepted=[]; skipped=0
    for story in stories:
        if not story.get("title") or not story.get("link") or is_duplicate(story,seen): skipped+=1; continue
        accepted.append(story); seen.append(story)
    return accepted,skipped
