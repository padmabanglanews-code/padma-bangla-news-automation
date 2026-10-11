from .normalize import normalize_text
WB_TERMS=("west bengal","পশ্চিমবঙ্গ","কলকাতা","হাওড়া","হুগলি","নদিয়া","মুর্শিদাবাদ","মালদা","দমদম","উত্তর ২৪ পরগনা")
INDIA_TERMS=("india","ভারত","নয়াদিল্লি","নতুন দিল্লি")
CATEGORY_TERMS={"politics":("election","minister","সরকার","নির্বাচন","মন্ত্রী","রাজনীতি"),"government":("government","প্রশাসন","সরকারি"),"crime":("police","court","arrest","পুলিশ","আদালত","গ্রেফতার"),"education":("school","university","পরীক্ষা","শিক্ষা","স্কুল"),"business":("business","market","ব্যবসা","বাজার"),"health":("health","hospital","স্বাস্থ্য","হাসপাতাল"),"sports":("cricket","football","খেলা","ক্রিকেট","ফুটবল"),"technology":("technology","tech","প্রযুক্তি"),"entertainment":("film","cinema","বিনোদন","সিনেমা")}
def rank_story(story: dict) -> dict:
    text=normalize_text(" ".join(str(story.get(k,"")) for k in ("title","description","category")))
    region="west_bengal" if any(t in text for t in WB_TERMS) else ("india" if any(t in text for t in INDIA_TERMS) else "international")
    category=str(story.get("category","")).strip().lower()
    if category not in CATEGORY_TERMS: category=next((n for n,terms in CATEGORY_TERMS.items() if any(t in text for t in terms)),"local_news")
    score={"west_bengal":300,"india":200,"international":100}[region] + (20 if category in {"politics","government","crime","education","business","health"} else 0)
    return {**story,"region":region,"category":category,"rank_score":score}
def rank_stories(stories: list[dict]) -> list[dict]:
    return sorted((rank_story(s) for s in stories),key=lambda s:(-s["rank_score"],str(s.get("published","")),str(s.get("title","")).casefold()))
