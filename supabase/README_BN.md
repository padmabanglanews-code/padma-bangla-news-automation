# Supabase storage setup — বাংলা

এই প্রস্তুতি Render-এর অস্থায়ী ফাইলের বদলে Supabase Postgres-এ Dashboard draft ও review status রাখার জন্য। এই ধাপে Supabase project তৈরি, SQL চালানো, secret যোগ করা বা Render deploy করা হয়নি।

## ১. Free project
1. Supabase-এর অফিসিয়াল সাইটে account খুলে Free project তৈরি করো।
2. Free plan-এ database 500 MB এবং সর্বোচ্চ 2টি active free project রয়েছে। 7 দিন পর্যাপ্ত activity না থাকলে project pause হতে পারে; এটিকে guaranteed always-on storage ভাববে না।
3. Project dashboard → SQL Editor খুলে repository-র `supabase/schema.sql` ফাইলের SQL paste করে Run করো।
4. Table Editor-এ `dashboard_drafts` table তৈরি হয়েছে কি না দেখো। এখানে কোনও news draft স্বয়ংক্রিয়ভাবে যোগ করা হয় না।

## ২. Render environment variables
Render web service তৈরি/কনফিগার করার সময় Environment-এ এই variables যোগ করতে হবে:
- `SUPABASE_URL` — Supabase Project URL
- `SUPABASE_SERVICE_ROLE_KEY` — Supabase server-side service role key; শুধু Render secret field-এ রাখবে
- `PADMA_DASHBOARD_TOKEN` — random secret, অন্তত 24 characters

**কোনও key বা token GitHub file, screenshot, বা ChatGPT chat-এ পাঠাবে না।** Browser UI-তে service role key কখনও দেওয়া যাবে না। SQL schema-তে RLS চালু এবং anon/authenticated policy নেই।

## ৩. নিরাপত্তা ও সীমা
- `manager/render_app.py` Supabase credentials না থাকলে startup-এ fail-closed করে; ephemeral JSON store-এ fallback করে না।
- Hosted API এখনও read-only GET endpoints; কোনও Run/Approve/Publish route নেই। Supabase store-এর review method server-side adapter হিসেবে আছে, কিন্তু HTTP API দিয়ে তা invoke করা যায় না।
- Free Supabase project 7 দিনের কম activity-তে pause হতে পারে। Database 500 MB সীমা; backups Free plan-এ অন্তর্ভুক্ত নয়। প্রয়োজনীয় draft data আলাদাভাবে export/backup করার ব্যবস্থা ভবিষ্যতে করতে হবে।
- কোনও live RSS/OpenRouter/Blogger request, draft creation বা publishing এই preparation-এ করা হয়নি.
- Deploy করার আগে GitHub Actions-এর manual offline tests-এ Success দেখতে হবে; এই changes-এর tests এখনও চালানো হয়নি।

Official references:
- https://supabase.com/pricing
- https://supabase.com/docs/guides/platform/free-project-pausing
- https://supabase.com/docs/guides/database/connecting-to-postgres
