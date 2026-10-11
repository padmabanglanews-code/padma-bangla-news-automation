# ড্যাশবোর্ড প্রোটোটাইপ (ধাপ ক) — শুধু DEMO DATA

- সব তথ্য কাল্পনিক নমুনা। কোনো লাইভ সংযোগ, API key, টোকেন বা secret নেই।
- কোনো নেটওয়ার্ক কল নেই, কিছু সংরক্ষিত হয় না।
- ড্যাশবোর্ড থেকে workflow চালানো বা সেটিংস বদলানো যায় না। "GitHub Actions খুলুন" বোতাম শুধু লিংক।

## ফাইল
| ফাইল | কাজ |
|---|---|
| `preview-standalone.html` | ফোনে সরাসরি খুলে দেখার একক ফাইল |
| `blogger-paste.html` | Blogger পেজের **HTML ভিউতে** পেস্ট করার একক ফাইল |
| `index.html`, `style.css`, `app.js`, `demo-data.js` | রিপোজিটরির উৎস ফাইল |
| `build_blogger_paste.py` | উৎস থেকে উপরের দুটি একক ফাইল বানায় |

## Android-এ প্রিভিউ
**উপায় ১ (সবচেয়ে সহজ):** `preview-standalone.html` ফোনে ডাউনলোড করুন → Files অ্যাপে ফাইলটিতে ট্যাপ → Chrome-এ খুলুন।
**উপায় ২ (Blogger):** Blogger → Pages → New page → HTML view → `blogger-paste.html`-এর পুরো লেখা পেস্ট → **Preview** (প্রকাশ করবেন না)।
