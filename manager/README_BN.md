# Padma Bangla News Manager — ধাপ C

এই অংশে RSS/Atom XML parser-এর পাশাপাশি একটি opt-in HTTPS RSS fetcher যোগ করা হয়েছে।

## পরীক্ষা
Repository root থেকে চালান:
`python -m unittest discover -s manager_tests -v`

## RSS fetcher-এর নিরাপত্তা
- `manager/live_rss.py`-এর `fetch_feed_xml()` কেবল সরাসরি কল করলে নেটওয়ার্কে যায়।
- HTTPS বাধ্যতামূলক; localhost/private/non-public IP host প্রত্যাখ্যান করা হয়।
- Redirect-এর চূড়ান্ত URL-ও পুনরায় যাচাই হয়।
- ডিফল্ট timeout ১০ সেকেন্ড, response limit ১ MB।
- ফাইলটি বর্তমান pipeline বা scheduled workflow থেকে কল করা হয় না।
- এই ধাপে RSS URL-এর curated তালিকা, স্বয়ংক্রিয় polling, OpenRouter, Blogger API বা publishing যুক্ত হয়নি।

## নিরাপত্তা ও পুরোনো সিস্টেম
- পুরোনো `scripts/`, `tests/`, `data/news_queue.json` এবং scheduled workflow অপরিবর্তিত।
- Manager pipeline এখনও dry-run; Blogger-এ কোনও draft বা post তৈরি করে না।
- নতুন fetcher-এর পরীক্ষা network request mock করে; প্রকৃত RSS feed-এ সংযোগ করে না।
