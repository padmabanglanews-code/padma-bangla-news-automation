"""Offline-capable RSS/Atom parser; no network fetching in Stage B."""
import re
import xml.etree.ElementTree as ET
from html import unescape

def _text(node, names):
    for child in node.iter():
        if child.tag.rsplit("}",1)[-1].lower() in names and child.text: return unescape(child.text.strip())
    return ""
def _link(node):
    for child in node.iter():
        if child.tag.rsplit("}",1)[-1].lower()=="link":
            href=child.attrib.get("href","").strip()
            if href and child.attrib.get("rel","alternate") in {"alternate",""}: return href
            if child.text and child.text.strip(): return child.text.strip()
    return ""
def parse_feed(xml_text: str, *, source: str="", category: str="general") -> list[dict]:
    if not isinstance(xml_text,str) or not xml_text.strip(): return []
    try: root=ET.fromstring(xml_text)
    except ET.ParseError as exc: raise ValueError("Malformed RSS/Atom XML") from exc
    result=[]
    for node in root.iter():
        if node.tag.rsplit("}",1)[-1].lower() not in {"item","entry"}: continue
        title=_text(node,{"title"}); link=_link(node)
        if not title or not link: continue
        result.append({"title":re.sub(r"\s+"," ",title),"link":link,"description":_text(node,{"description","summary","encoded","content"}),"published":_text(node,{"pubdate","published","updated","date"}),"source":source,"category":category})
    return result
