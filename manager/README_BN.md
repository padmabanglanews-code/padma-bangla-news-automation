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


## Stage J — Dashboard UI mock integration

- `dashboard/manager-preview.html` ও `dashboard/manager-preview.js` একটি আলাদা mock-only draft review screen।
- এটি Stage I snapshot-এর মতো data shape দেখায়: draft title/summary/source, quality status/errors/warnings এবং review status।
- ইচ্ছাকৃতভাবে approve/publish action নেই; কোনও network request, browser storage বা backend call নেই।
- এটি বিদ্যমান `dashboard/index.html` ও `dashboard/app.js` বদলায়নি; পুরোনো prototype অক্ষত।
- মোবাইল ব্রাউজারে preview দেখতে GitHub repository-তে `dashboard/manager-preview.html` খুলে Raw নয়, Pages/server preview দরকার; সরাসরি repository file viewer-এ JavaScript app নাও চলতে পারে।
- এটি Live Dashboard Connection নয়। পরবর্তী ধাপে secure hosting, authentication ও persistent backend প্রয়োজন।


## Stage K — Integrated pipeline (explicit opt-in)

- `manager/integrated_pipeline.py` RSS → AI draft candidate → editorial quality check → optional Blogger Draft flow একত্রিত করে।
- Default call কোনও live RSS, OpenRouter বা Blogger request করে না; `integration-safe-idle` ফল দেয়।
- Live চালাতে caller-কে স্পষ্টভাবে `live_rss=True` দিতে হবে; AI-এর জন্য `generate_ai=True`; Blogger Draft তৈরির জন্য অতিরিক্তভাবে `create_blogger_drafts=True` দিতে হবে।
- Blogger-এ পাঠানোর আগে QC pass আবশ্যক। QC fail হলে Blogger call বাদ যায়।
- এই pipeline-এ কোনও publish function নেই; সব ফলাফলে `published=false`।
- নতুন tests mock RSS, AI এবং Blogger creator ব্যবহার করে; GitHub Actions-এ চালানোর আগে ফলাফল যাচাই করতে হবে। বাস্তব service credentials বা live calls এখানে পরীক্ষা করা হয়নি।


## Stage L1 — Persistent Dashboard Draft Store

- `manager/persistent_dashboard.py` আলাদা JSON ফাইলে Dashboard draft ও review status atomicভাবে সংরক্ষণ করে; নতুন store instance তৈরি করলেও draft থাকে।
- ডিফল্ট ফাইল `manager/data/dashboard_drafts.json`; এটি পুরোনো `data/news_queue.json` বা manager history ফাইল স্পর্শ করে না।
- JSON ফাইল corrupt/ভুল schema হলে store overwrite না করে error দেয়।
- Quality check fail হলে approve করা যায় না; approve শুধু editorial status, Blogger call বা publish নয়।
- এটি এখনও local Python service adapter: HTTP server, dashboard UI connection, authentication বা multi-process locking নেই। তাই এটিকে public internet-এ সরাসরি প্রকাশ করা যাবে না।
- Tests temporary directory ও mock data ব্যবহার করে; live service call নেই।


## Stage L2 — Dashboard cycle service facade

- `manager/dashboard_service.py` একবারের Dashboard cycle চালানোর facade: নির্বাচিত pipeline চালায়, AI candidate আলাদা persistent store-এ সংরক্ষণ করে এবং read-only snapshot ফেরত দেয়।
- Default mode `integration-safe-idle`; RSS/AI/Blogger live effect চালু হয় না। Live কাজের জন্য সংশ্লিষ্ট explicit flags দিতে হয়।
- Stable SHA-256 ID একই source URL ও title-এর candidate পুনরায় এলে duplicate আটকাতে সাহায্য করে।
- এই ধাপে কোনও scheduler, HTTP endpoint, login/authentication বা live dashboard connection তৈরি হয়নি। তাই এখনই public web app হিসেবে expose করা যাবে না।
- Tests mock RSS/AI এবং temporary storage ব্যবহার করে। Workflow Success না দেখা পর্যন্ত এই ধাপের tests-কে সফল বলা যাবে না।


## Stage L3 — Authenticated read-only HTTP API

- `manager/dashboard_http.py` loopback-only read-only API দেয়: `GET /api/dashboard`, `GET /api/drafts`, `GET /health`।
- `PADMA_DASHBOARD_TOKEN` configure না থাকলে API বন্ধ থাকে; প্রতিটি request-এ `Authorization: Bearer <token>` দরকার।
- API শুধু GET গ্রহণ করে; POST/PUT/DELETE ও অজানা route প্রত্যাখ্যান করে। কোনও RSS/AI/Blogger cycle trigger, approval বা publishing endpoint নেই।
- Server চালানোর helper `serve_local_dashboard()`; default bind `127.0.0.1:8765` এবং non-loopback bind প্রত্যাখ্যান করে।
- এটি স্থানীয় পরীক্ষার জন্য। Public internet-এ expose করা যাবে না; production-এর জন্য HTTPS, proper authentication/authorization, rate limiting, CSRF strategy এবং deployment hardening দরকার।
- Tests offline WSGI calls ব্যবহার করে; server start বা external API call করে না।


## Stage L4 — Read-only Dashboard UI adapter

- `dashboard/manager-live-adapter.html` ও `dashboard/manager-live-adapter.js` একই-origin `GET /api/dashboard` endpoint-এর read-only UI adapter।
- Token password input-এ নেওয়া হয় এবং শুধু page memory-তে থাকে; localStorage, URL বা source code-এ লেখা হয় না। Disconnect করলে field ও token মুছে যায়।
- এটি কেবল dashboard metrics ও draft cards দেখায়; কোনও Run, Approve, Blogger বা Publish action নেই।
- এটি এখনও backend-এর সঙ্গে deployed/live connected নয়। কাজ করতে UI ও API-কে একই origin-এ নিরাপদভাবে host/reverse-proxy করতে হবে; GitHub repository file viewer বা GitHub Pages থেকে local loopback API-তে সরাসরি সংযোগ ধরে নেওয়া যাবে না।
- API token কোনও screenshot বা chat-এ পাঠাবে না। Live use-এর আগে secure hosting/auth configuration দরকার।


## Stage L5 — Dashboard adapter static safety tests

- `manager_tests/test_dashboard_adapter_static.py` HTML asset references এবং JavaScript-এর read-only request pattern পরীক্ষা করে।
- Test-গুলো নিশ্চিত করে adapter `GET /api/dashboard` ব্যবহার করে, browser storage বা `innerHTML` ব্যবহার করে না এবং Publish/Run/Approve endpoint উল্লেখ করে না।
- এগুলো static/offline checks; browser-এ UI render হয়েছে বা বাস্তব API connection কাজ করেছে—এমন প্রমাণ নয়।


## Stage L7 — Local dashboard runner

- `manager/run_dashboard.py` local read-only dashboard চালানোর CLI entry point।
- চালানোর আগে environment-এ অন্তত ২৪ অক্ষরের `PADMA_DASHBOARD_TOKEN` সেট করতে হবে; token source code বা GitHub file-এ রাখবে না।
- চালানোর কমান্ড: `python -m manager.run_dashboard`; ঐচ্ছিক port-এর জন্য `PADMA_DASHBOARD_PORT` ব্যবহার করা যায়।
- Server শুধু `127.0.0.1`-এ bind করে; এটি public hosting নয় এবং অন্য ডিভাইস থেকে সরাসরি ব্যবহার করা যাবে না।
- Android-এ GitHub Actions সফল হওয়া মানে তোমার ফোনে server চালু হয়েছে—এমন নয়। বাস্তব ব্যবহার করতে আলাদা host/deployment প্রয়োজন।
- এই runner কোনও schedule, RSS collection, AI call, Blogger draft creation বা publishing চালু করে না।
