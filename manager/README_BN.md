# Padma Bangla News Manager — ধাপ খ

এটি পুরোনো pipeline থেকে আলাদা, offline-first ভিত্তি। এই ধাপে কোনও নেটওয়ার্ক কল, OpenRouter কল, Blogger API কল বা প্রকাশনা নেই।

## পরীক্ষা
Repository root থেকে চালান: python -m unittest discover -s manager_tests -v

## নিরাপত্তা
- পুরোনো scripts/, tests/, data/news_queue.json এবং workflow অপরিবর্তিত।
- নতুন ইতিহাসের পথ manager/data/history.json; এই ধাপে pipeline নিজে ইতিহাস লেখে না।
- RSS XML ইনপুট হিসেবে সরাসরি দেওয়া হয়; live RSS fetching পরবর্তী অনুমোদিত ধাপে হবে।
- কোনও Secret প্রয়োজন নেই।
