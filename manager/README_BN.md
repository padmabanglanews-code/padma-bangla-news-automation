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

## Stage E — Blogger Draft-only client

- `manager/blogger_drafts.py` Blogger API v3-তে draft তৈরির client।
- `isDraft=true` request URL-এ client নিজেই বাধ্যতামূলক করে; publish method নেই।
- Environment variables: `BLOGGER_ACCESS_TOKEN`, `BLOGGER_BLOG_ID`।
- Token chat বা source code-এ লিখবে না; secret store/local environment ব্যবহার করবে।
- শুধু `create_blogger_draft()` স্পষ্টভাবে কল করলে Blogger-এ draft তৈরি হবে। এই ধাপে কোনও live Blogger request করা হয়নি।
- Tests fake HTTP opener ব্যবহার করে; বাস্তব Blogger account-এ কিছু তৈরি করে না।
- Blogger API-তে draft তৈরি করার জন্য OAuth access token দরকার; token নিজে থেকে এখানে তৈরি বা refresh করা হয় না।

## Stage F — End-to-end dry-run orchestration

- `manager/end_to_end.py` RSS collect → dedupe/ranking → AI draft candidate একসঙ্গে চালানোর orchestrator।
- Tests RSS ও AI-তে mock ব্যবহার করে; প্রকৃত network/API call হয় না।
- Blogger client ইচ্ছাকৃতভাবে orchestration-এর মধ্যে যুক্ত নয়; `blogger_contacted=false`, `blogger_draft_created=false`, `published=false` থাকে।
- বাস্তব feed fetch বা OpenRouter call কেবল caller স্পষ্টভাবে dependency হিসেবে না দিলে নয়; তবে default AI generator real client, তাই production API চালানোর আগে mock generator ব্যবহার করো।
- এই ধাপে live end-to-end execution করা হয়নি।


## Stage G — News Verification & Quality Control

- `manager/verification.py` draft-এর title, body, summary, source URL এবং placeholder/AI meta-text-এর মতো নির্দিষ্ট quality signal পরীক্ষা করে।
- Batch রিপোর্টে প্রতিটি candidate-এর `passed`, `errors`, `warnings` এবং `factual_accuracy_verified=false` থাকে।
- এটি নির্দিষ্ট কাঠামো ও quality signal যাচাই করে; খবর সত্য কি না তা স্বাধীনভাবে প্রমাণ করে না। প্রকাশের আগে সম্পাদককে মূল সূত্রের সঙ্গে তথ্য মিলিয়ে নিতে হবে।
- কোনও network/API call, Blogger access, Facebook post বা publishing নেই। সব output `published: false`।
- নতুন tests শুধু offline unit tests; চালানোর কমান্ড: `python -m unittest discover -s manager_tests -v`।


## Stage H — Dashboard draft service layer (offline)

- `manager/dashboard_api.py` in-memory draft list/detail ও editorial approve/reject action-এর ভিত্তি।
- এটি এখন HTTP server নয়; ভবিষ্যৎ authenticated dashboard adapter-এর জন্য service layer মাত্র।
- Approve মানে শুধু `approved_for_manual_next_step`; এটি Blogger-এ পাঠায় না এবং publish করে না।
- Quality check fail হলে approve প্রত্যাখ্যান হয়; প্রতিটি action-এর পরে `published=false` থাকে।
- Draft store বর্তমানে memory-তে থাকে; process restart হলে data থাকে না। Production dashboard-এ যুক্ত করার আগে authentication, authorization, persistent storage, CSRF/rate limits এবং audit logging প্রয়োজন।
- Tests offline; কোনও external API বা publishing নেই।


## Stage I — Read-only Dashboard snapshot

- `manager/dashboard_readonly.py` সরবরাহ করা draft list থেকে JSON-serializable read-only snapshot তৈরি করে।
- Dashboard-এ draft title, summary, source URL, review status, quality pass/fail, errors/warnings ও pipeline status দেখানোর জন্য data shape দেয়।
- এটি নিজে কোনও HTTP server চালায় না, storage থেকে নিজে data load করে না, external API কল করে না।
- Input-এর `published` flag উপেক্ষা করে output-এ সবসময় `published=false` রাখে; কোনও approval বা publishing action নেই।
- Tests offline; কোনও Blogger, OpenRouter বা Facebook request নেই।
- Live dashboard connection-এর আগে authenticated hosting, access control, persistent store ও UI integration আলাদাভাবে তৈরি/পরীক্ষা করতে হবে।
