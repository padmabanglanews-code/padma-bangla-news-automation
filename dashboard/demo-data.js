/* DEMO DATA — সবই কাল্পনিক নমুনা। কোনো সত্যিকারের খবর, সূত্র বা সংখ্যা নয়।
   এখানে কোনো API key, token বা secret নেই এবং রাখা উচিত নয়। */
window.PADMA_DEMO = {
  label: 'DEMO DATA',
  updated: '২০২৬-১০-১১ ০৯:০০ IST (নমুনা)',
  metrics: [
    { label: 'আবিষ্কৃত খবর', en: 'Stories discovered', value: '124' },
    { label: 'নির্বাচিত', en: 'Stories selected', value: '18' },
    { label: 'ডুপ্লিকেট বাদ', en: 'Duplicates skipped', value: '41' },
    { label: 'প্রতিবেদন তৈরি', en: 'Articles generated', value: '12' },
    { label: 'Blogger ড্রাফট', en: 'Drafts created', value: '9' },
    { label: 'ব্যর্থ কাজ', en: 'Failed jobs', value: '3' },
    { label: 'শেষ সফল রান', en: 'Last successful run', value: '১১ অক্টো, ০৭:৩০' },
    { label: 'পরবর্তী রান', en: 'Next scheduled run', value: 'নির্ধারিত নয় (শিডিউল বন্ধ)' }
  ],
  queue: [
    { id: 'Q-001', title: 'কলকাতায় ভারী বৃষ্টির পূর্বাভাস, নিচু এলাকায় জলজমের আশঙ্কা', source: 'নমুনা সূত্র ১', category: 'স্থানীয়', geo: 'পশ্চিমবঙ্গ', status: 'selected', score: 152, verification: 'একটি সূত্র', time: '০৮:১০' },
    { id: 'Q-002', title: 'উচ্চমাধ্যমিক পরীক্ষার নতুন সময়সূচি প্রকাশ', source: 'নমুনা সূত্র ২', category: 'শিক্ষা', geo: 'পশ্চিমবঙ্গ', status: 'draft', score: 148, verification: 'একাধিক সূত্রে অনুরূপ খবর', time: '০৭:৪৫' },
    { id: 'Q-003', title: 'রাজ্যে শিক্ষক নিয়োগ প্রক্রিয়া নিয়ে নতুন নির্দেশ', source: 'নমুনা সূত্র ১', category: 'চাকরি', geo: 'পশ্চিমবঙ্গ', status: 'needs_review', score: 141, verification: 'যাচাই বাকি', time: '০৭:২০' },
    { id: 'Q-004', title: 'শেয়ার বাজারে সামান্য উত্থান, সেনসেক্স-নিফটি স্থিতিশীল', source: 'নমুনা সূত্র ৩', category: 'ব্যবসা', geo: 'ভারত', status: 'queued', score: 96, verification: 'একটি সূত্র', time: '০৬:৫০' },
    { id: 'Q-005', title: 'কলকাতায় ভারী বৃষ্টির আশঙ্কা, সতর্কতা জারি', source: 'নমুনা সূত্র ৪', category: 'স্থানীয়', geo: 'পশ্চিমবঙ্গ', status: 'duplicate', score: 140, verification: 'Q-001-এর সদৃশ', time: '০৬:৩০' },
    { id: 'Q-006', title: 'আন্তর্জাতিক সম্মেলনে জলবায়ু প্রতিশ্রুতি নিয়ে আলোচনা', source: 'নমুনা সূত্র ৫', category: 'আন্তর্জাতিক', geo: 'আন্তর্জাতিক', status: 'queued', score: 70, verification: 'একটি সূত্র', time: '০৫:৫৫' },
    { id: 'Q-007', title: 'জেলা হাসপাতালে নতুন চিকিৎসা পরিষেবা চালু', source: 'নমুনা সূত্র ২', category: 'স্বাস্থ্য', geo: 'পশ্চিমবঙ্গ', status: 'failed', score: 130, verification: 'নেই', time: '০৫:১০' }
  ],
  writer: {
    storyId: 'Q-001',
    sourceNote: 'নমুনা সূত্র ১ — https://example.com/demo-1 (কাল্পনিক URL)',
    headline: 'কলকাতায় ভারী বৃষ্টির পূর্বাভাস, নিচু এলাকায় জলজমের আশঙ্কা',
    summary: 'আবহাওয়া দপ্তরের বরাতে জানা গেছে, আগামী দু’দিন কলকাতা ও আশপাশে ভারী বৃষ্টির সম্ভাবনা রয়েছে।',
    paragraphs: [
      'সূত্রের খবর অনুযায়ী, আগামী দু’দিন কলকাতা ও লাগোয়া এলাকায় ভারী বৃষ্টির পূর্বাভাস দেওয়া হয়েছে। (নমুনা অনুচ্ছেদ)',
      'নিচু এলাকায় জল জমার আশঙ্কার কথা বলা হয়েছে। প্রশাসনের পক্ষ থেকে কোনো আনুষ্ঠানিক বিবৃতির উল্লেখ মূল প্রতিবেদনে নেই। (নমুনা অনুচ্ছেদ)'
    ],
    verification: 'single_source',
    reviewNotes: 'শুধু একটি সূত্র। বৃষ্টির পরিমাণ ও তারিখ আবহাওয়া দপ্তরের মূল বিজ্ঞপ্তির সঙ্গে মিলিয়ে নিন। (নমুনা)'
  },
  seo: {
    title: 'কলকাতায় ভারী বৃষ্টির পূর্বাভাস: জলজমের আশঙ্কা',
    description: 'আগামী দু’দিন কলকাতা ও আশপাশে ভারী বৃষ্টির সম্ভাবনা। নিচু এলাকায় জলজমের আশঙ্কা নিয়ে সর্বশেষ তথ্য।',
    slug: 'kolkata-heavy-rain-forecast',
    labels: 'স্থানীয়, আবহাওয়া, কলকাতা',
    mainKeyword: 'কলকাতা বৃষ্টি',
    related: 'জলজমে, আবহাওয়ার পূর্বাভাস, পশ্চিমবঙ্গ'
  },
  images: [
    { id: 'I-01', story: 'Q-001', status: 'valid', source: 'নমুনা সূত্র ১ (এমবেডেড/RSS)', rights: 'ব্যবহারের অনুমতি যাচাই বাকি', check: 'HTTP 200 • image/jpeg • ১৮০ KB', alt: 'কলকাতার রাস্তায় বৃষ্টির দৃশ্য (নমুনা বিবরণ)' },
    { id: 'I-02', story: 'Q-002', status: 'valid', source: 'নমুনা সূত্র ২', rights: 'ব্যবহারের অনুমতি যাচাই বাকি', check: 'HTTP 200 • image/png • ৯০ KB', alt: 'পরীক্ষার্থীদের নমুনা ছবি' },
    { id: 'I-03', story: 'Q-003', status: 'awaiting', source: '—', rights: '—', check: 'উপযুক্ত ছবি পাওয়া যায়নি; কিছু বানানো হয়নি', alt: '' },
    { id: 'I-04', story: 'Q-007', status: 'failed', source: 'নমুনা সূত্র ২', rights: '—', check: 'ব্যর্থ: কনটেন্ট-টাইপ text/html (ছবি নয়)', alt: '' }
  ],
  feeds: [
    { name: 'নমুনা ফিড — পশ্চিমবঙ্গ ১', url: 'https://example.com/feed-wb-1.xml', region: 'পশ্চিমবঙ্গ', enabled: true, last: 'ঠিক আছে • ২০টি আইটেম', checked: '০৮:০০' },
    { name: 'নমুনা ফিড — পশ্চিমবঙ্গ ২', url: 'https://example.com/feed-wb-2.xml', region: 'পশ্চিমবঙ্গ', enabled: true, last: 'ঠিক আছে • ১৫টি আইটেম', checked: '০৮:০০' },
    { name: 'নমুনা ফিড — ভারত', url: 'https://example.com/feed-in.xml', region: 'ভারত', enabled: true, last: 'ঠিক আছে • ৩০টি আইটেম', checked: '০৮:০০' },
    { name: 'নমুনা ফিড — আন্তর্জাতিক', url: 'https://example.com/feed-world.xml', region: 'আন্তর্জাতিক', enabled: true, last: 'ধীর সাড়া • ১২টি আইটেম', checked: '০৮:০১' },
    { name: 'নমুনা ফিড — বন্ধ', url: 'https://example.com/feed-off.xml', region: 'ভারত', enabled: false, last: 'বন্ধ রাখা', checked: '—' },
    { name: 'নমুনা ফিড — ভুল', url: 'https://example.com/feed-broken.xml', region: 'পশ্চিমবঙ্গ', enabled: true, last: 'ত্রুটি: অবৈধ XML', checked: '০৮:০১' }
  ],
  runs: [
    { id: 'RUN-0005', mode: 'dry-run', start: '১১ অক্টো ০৭:৩০', end: '০৭:৩২', collected: 38, dups: 12, generated: 0, drafts: 0, status: 'ok' },
    { id: 'RUN-0004', mode: 'draft', start: '১০ অক্টো ১৯:৩০', end: '১৯:৩৪', collected: 41, dups: 15, generated: 3, drafts: 3, status: 'ok' },
    { id: 'RUN-0003', mode: 'draft', start: '১০ অক্টো ১৩:৩০', end: '১৩:৩১', collected: 35, dups: 9, generated: 1, drafts: 0, status: 'failed' },
    { id: 'RUN-0002', mode: 'dry-run', start: '১০ অক্টো ০৮:০০', end: '০৮:০২', collected: 30, dups: 5, generated: 0, drafts: 0, status: 'ok' }
  ],
  errors: [
    { cat: 'রান ব্যর্থ', code: 'quota_exhausted', msg: 'কনফিগার করা মডেলের কোটা শেষ (নমুনা)', count: 1, fix: ['OpenRouter ড্যাশবোর্ডে কোটা/ব্যালান্স দেখুন।', 'অন্য ফ্রি মডেল বেছে GitHub secret/variable OPENROUTER_MODEL বদলান — কোড বদলাতে হবে না।', 'সিস্টেম নিজে থেকে পেইড মডেলে যাবে না।'] },
    { cat: 'অবৈধ RSS', code: 'invalid_rss', msg: 'ফিড XML পার্স করা যায়নি (নমুনা)', count: 1, fix: ['ব্রাউজারে ফিড URL খুলে দেখুন।', 'সঠিক URL বসান বা ফিডটি বন্ধ রাখুন।'] },
    { cat: 'Blogger অনুমতি', code: 'blogger_auth', msg: 'অনুমতি/টোকেন অবৈধ (নমুনা)', count: 1, fix: ['Blogger OAuth আবার অনুমোদন করুন।', 'নতুন secret শুধু GitHub Actions Secrets-এ বসান — চ্যাটে বা ব্লগে নয়।', 'ঠিক না হওয়া পর্যন্ত ড্রাফট তৈরি বন্ধ থাকবে।'] },
    { cat: 'API কী', code: 'invalid_api_key', msg: 'OpenRouter কী প্রত্যাখ্যাত (নমুনা)', count: 0, fix: ['OPENROUTER_API_KEY secret-টি নতুন কী দিয়ে বদলান।'] },
    { cat: 'GitHub Actions', code: 'actions_failure', msg: 'workflow শুরুতেই থেমেছে (নমুনা)', count: 0, fix: ['Actions → রানটি খুলে লাল ধাপের লগ দেখুন।', 'লগে কোনো secret থাকার কথা নয়; থাকলে সঙ্গে সঙ্গে সেটি বদলান।'] }
  ],
  actionsUrl: 'https://github.com/padmabanglanews-code/padma-bangla-news-automation/actions'
};
