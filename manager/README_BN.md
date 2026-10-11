# Padma Bangla News Manager — ধাপ C

এই ধাপে curated RSS উৎসের তালিকা এবং opt-in live RSS collection যুক্ত হয়েছে।

## নির্বাচিত RSS উৎস
উৎসের URL এবং enable/disable অবস্থা `manager/feed_sources.json`-এ রাখা হয়েছে:
- The Hindu — Kolkata
- Live Hindustan — West Bengal
- ABP News — India ও States
- Press Information Bureau — Press Releases
- The Hindu — International

এই উৎসগুলোর ঠিকানা প্রকাশ্য RSS তালিকা থেকে নেওয়া হয়েছে; এই পরিবর্তনে বাস্তবে feed fetch করে availability যাচাই করা হয়নি।

## কীভাবে কাজ করে
- `manager/live_rss.py`-এর `fetch_feed_xml()` HTTPS feed সংগ্রহ করে; timeout ১০ সেকেন্ড ও সর্বোচ্চ ১ MB।
- `manager/live_pipeline.py`-এর `collect_live_rss()` শুধু সরাসরি কল করলে enabled feed fetch করে, তারপর বিদ্যমান parser/dedupe/ranking চালায়।
- Feed ব্যর্থ হলে অন্য feed চেষ্টা করা হয় এবং error ফলাফলে রাখা হয়।
- ফলাফল সবসময় dry-run; `published: false`। Blogger, OpenRouter বা Facebook-এ কোনও কল নেই।
- এই collection existing scheduled workflow থেকে কল করা হয় না; স্বয়ংক্রিয় polling চালু হয়নি।

## পরীক্ষা
Repository root থেকে চালান:
`python -m unittest discover -s manager_tests -v`
নতুন live-pipeline tests mock fetcher ব্যবহার করে; বাস্তব feed URL-এ সংযোগ করে না।

## নিরাপত্তা ও পুরোনো সিস্টেম
- HTTPS বাধ্যতামূলক; localhost/private/non-public IP host প্রত্যাখ্যান করা হয় এবং redirect-এর চূড়ান্ত URL পুনরায় যাচাই হয়।
- পুরোনো `scripts/`, `tests/`, `data/news_queue.json` এবং scheduled workflow অপরিবর্তিত।
- এই ধাপে OpenRouter বা Blogger Draft integration নেই।

## Stage D — OpenRouter draft candidate

- `manager/openrouter_client.py` OpenRouter Chat Completions-এ কেবল স্পষ্টভাবে কল করলে অনুরোধ পাঠায়।
- প্রয়োজনীয় environment variable: `OPENROUTER_API_KEY` এবং `OPENROUTER_MODEL`।
- API key chat, source code বা repository file-এ লিখবে না; GitHub Actions Secret বা স্থানীয় environment variable ব্যবহার করবে।
- `manager/draft_pipeline.py` candidate খসড়া ফেরত দেয়। Blogger/Facebook integration বা publication করে না।
- Mock tests-এ কোনও প্রকৃত API request করা হয় না।
- AI-এর তৈরি লেখা প্রকাশের আগে সম্পাদকীয় যাচাই প্রয়োজন; verification notes রাখা হয়।
