import json
import urllib.request
import xml.etree.ElementTree as ET

FEEDS = {
    "abp_home": "https://bengali.abplive.com/home/feed",
    "abp_kolkata": "https://bengali.abplive.com/news/kolkata/feed",
    "abp_states": "https://bengali.abplive.com/states/feed",
    "abp_india": "https://bengali.abplive.com/news/india/feed",
    "abp_world": "https://bengali.abplive.com/news/world/feed",
    "abp_business": "https://bengali.abplive.com/business/feed",
    "abp_health": "https://bengali.abplive.com/health/feed",
    "abp_technology": "https://bengali.abplive.com/technology/feed",
    "abp_education": "https://bengali.abplive.com/education/feed",
}

def fetch_feed(category, url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "PadmaBanglaNews/1.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        root = ET.fromstring(response.read())

    items = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()

        if title and link:
            items.append({
                "category": category,
                "title": title,
                "link": link,
                "published": pub_date,
                "source": "ABP Ananda"
            })

    return items

def main():
    stories = []

    for category, url in FEEDS.items():
        try:
            stories.extend(fetch_feed(category, url))
        except Exception as error:
            print(f"RSS error [{category}]: {error}")

    print(json.dumps(stories, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
