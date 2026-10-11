/* Padma Bangla News — AI Manager dashboard (prototype v0.1)
   শুধু DEMO DATA দেখায়। কোনো নেটওয়ার্ক কল নেই, কোনো secret নেই, কিছু সংরক্ষণও হয় না। */
(function () {
  'use strict';
  var D = window.PADMA_DEMO;
  var root = document.getElementById('padma-dash');
  if (!root) { return; }
  if (!D) { root.textContent = 'Data unavailable (demo-data.js লোড হয়নি)'; return; }

  function h(tag, attrs, kids) {
    var e = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (k === 'class') { e.className = v; }
        else if (k === 'text') { e.textContent = v; }
        else if (k.indexOf('on') === 0) { e.addEventListener(k.slice(2), v); }
        else { e.setAttribute(k, v); }
      });
    }
    (kids || []).forEach(function (c) {
      if (c === null || c === undefined) { return; }
      e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return e;
  }
  function badge(text, cls) { return h('span', { class: 'pd-badge ' + (cls || ''), text: text }); }

  var STATUS = {
    queued: ['সারিতে', 'pd-b-info'], selected: ['নির্বাচিত', 'pd-b-ok'], draft: ['ড্রাফট তৈরি', 'pd-b-ok'],
    needs_review: ['পর্যালোচনা দরকার', 'pd-b-wait'], duplicate: ['ডুপ্লিকেট', ''], failed: ['ব্যর্থ', 'pd-b-bad']
  };
  var IMG = { valid: ['বৈধ', 'pd-b-ok'], awaiting: ['ছবির অপেক্ষায়', 'pd-b-wait'], failed: ['ব্যর্থ', 'pd-b-bad'] };

  function demoNote(text) { return h('div', { class: 'pd-note', text: 'DEMO DATA — ' + text }); }

  /* ---------- Overview ---------- */
  function overview() {
    var grid = h('div', { class: 'pd-grid' }, D.metrics.map(function (m) {
      return h('div', { class: 'pd-metric' }, [
        h('b', { text: m.value }), h('span', { text: m.label + ' / ' + m.en }),
        h('small', { text: 'সূত্র: DEMO DATA • হালনাগাদ: ' + D.updated })
      ]);
    }));
    return h('div', null, [
      h('h2', { text: 'Overview — সারসংক্ষেপ' }),
      h('div', { class: 'pd-note pd-warn', text: 'লাইভ ডেটা সংযুক্ত নয়। নিচের সব সংখ্যা নমুনা। সত্যিকারের ডেটা এলে এখানে "Data unavailable"-এর বদলে আসল সংখ্যা ও সূত্র দেখাবে।' }),
      grid,
      h('div', { class: 'pd-card', style: 'margin-top:12px' }, [
        h('h3', { text: 'লাইভ স্ট্যাটাস' }),
        h('div', { class: 'pd-row' }, [badge('Data unavailable', 'pd-b-bad'), h('span', { class: 'pd-meta', text: 'ব্যাকএন্ড এখনো তৈরি হয়নি।' })])
      ]),
      h('div', { class: 'pd-card' }, [
        h('h3', { text: 'কাজ চালানো' }),
        h('p', { class: 'pd-meta', text: 'নিরাপত্তার কারণে এই পাতা থেকে workflow চালানো বা সেটিংস বদলানো যায় না (ব্রাউজারে GitHub টোকেন রাখা নিরাপদ নয়)। নতুন Manager workflow এখনো যোগ হয়নি; নিচের লিংকটি শুধু GitHub Actions পাতা খোলে।' }),
        h('a', { class: 'pd-btn sec', href: D.actionsUrl, target: '_blank', rel: 'noopener noreferrer', text: 'GitHub Actions খুলুন ↗' })
      ])
    ]);
  }

  /* ---------- News Queue ---------- */
  var qFilter = 'all';
  function queue() {
    var wrap = h('div');
    var chips = h('div', { class: 'pd-chips' });
    var list = h('div');
    var opts = [['all', 'সব']].concat(Object.keys(STATUS).map(function (k) { return [k, STATUS[k][0]]; }));
    function draw() {
      chips.textContent = '';
      opts.forEach(function (o) {
        chips.appendChild(h('button', { class: 'pd-chip', type: 'button', 'aria-pressed': String(qFilter === o[0]), text: o[1], onclick: function () { qFilter = o[0]; draw(); } }));
      });
      list.textContent = '';
      var items = D.queue.filter(function (q) { return qFilter === 'all' || q.status === qFilter; });
      if (!items.length) { list.appendChild(h('div', { class: 'pd-empty', text: 'এই ফিল্টারে কোনো খবর নেই।' })); return; }
      items.forEach(function (q) {
        var s = STATUS[q.status];
        list.appendChild(h('div', { class: 'pd-card' }, [
          h('div', { class: 'pd-row' }, [badge(s[0], s[1]), badge(q.geo), badge(q.category), h('span', { class: 'pd-meta', text: q.id + ' • স্কোর ' + q.score })]),
          h('strong', { text: q.title }),
          h('div', { class: 'pd-meta', text: q.source + ' • ' + q.time + ' • যাচাই: ' + q.verification })
        ]));
      });
    }
    draw();
    wrap.appendChild(h('h2', { text: 'News Queue — খবরের সারি' }));
    wrap.appendChild(demoNote('শিরোনাম ও সূত্র কাল্পনিক। র‍্যাঙ্কিং স্কোর শুধু অগ্রাধিকারের ইঙ্গিত, তথ্য-যাচাই নয়।'));
    wrap.appendChild(chips); wrap.appendChild(list);
    return wrap;
  }

  /* ---------- AI Writer ---------- */
  function writer() {
    var w = D.writer;
    return h('div', null, [
      h('h2', { text: 'AI Writer — বাংলা প্রতিবেদন' }),
      demoNote('নিচের লেখাটি নমুনা, কোনো AI-এর আসল আউটপুট নয়।'),
      h('div', { class: 'pd-card' }, [
        h('h3', { text: 'উৎস (' + w.storyId + ')' }), h('p', { class: 'pd-meta', text: w.sourceNote }),
        h('div', { class: 'pd-row' }, [badge('যাচাই: ' + w.verification, 'pd-b-wait'), badge('মানুষের পর্যালোচনা বাধ্যতামূলক', 'pd-b-bad'), badge('শুধু ড্রাফট', 'pd-b-ok')])
      ]),
      h('div', { class: 'pd-card' }, [
        h('h3', { text: w.headline }), h('p', { class: 'pd-meta', text: w.summary })
      ].concat(w.paragraphs.map(function (p) { return h('p', { text: p }); }))),
      h('div', { class: 'pd-card' }, [h('h3', { text: 'পর্যালোচনা-নোট' }), h('p', { text: w.reviewNotes })]),
      h('button', { class: 'pd-btn', type: 'button', disabled: 'disabled', text: 'Generate — ব্যাকএন্ড সংযুক্ত নয়' }),
      h('p', { class: 'pd-meta', text: 'প্রকাশের কোনো বোতাম বা কোড এই সিস্টেমে থাকবে না। সব লেখা Blogger ড্রাফটেই যাবে।' })
    ]);
  }

  /* ---------- SEO ---------- */
  function seo() {
    var s = D.seo;
    function field(label, key, limit, multi) {
      var input = multi ? h('textarea', { 'aria-label': label }) : h('input', { type: 'text', 'aria-label': label });
      input.value = s[key];
      var cnt = h('div', { class: 'pd-count' });
      function upd() {
        var n = input.value.length;
        if (limit) { cnt.textContent = n + ' / ' + limit + ' অক্ষর'; cnt.className = 'pd-count' + (n > limit ? ' over' : ''); }
      }
      input.addEventListener('input', upd); upd();
      return h('div', null, [h('label', { text: label }), input, cnt]);
    }
    return h('div', null, [
      h('h2', { text: 'SEO Manager' }),
      demoNote('এখানের পরিবর্তন শুধু এই পাতায়, কিছুই সংরক্ষিত বা পাঠানো হয় না।'),
      h('div', { class: 'pd-card' }, [
        field('SEO শিরোনাম', 'title', 60, false),
        field('সার্চ বিবরণ', 'description', 155, true),
        field('URL slug (প্রস্তাব)', 'slug', 0, false),
        field('লেবেল', 'labels', 0, false),
        field('মূল কীওয়ার্ড', 'mainKeyword', 0, false),
        field('সম্পর্কিত কীওয়ার্ড', 'related', 0, false)
      ]),
      h('p', { class: 'pd-meta', text: 'SEO স্কোর র‍্যাঙ্কিংয়ের নিশ্চয়তা দেয় না; তথ্যের সঠিকতা সবসময় আগে।' })
    ]);
  }

  /* ---------- Images ---------- */
  function images() {
    return h('div', null, [
      h('h2', { text: 'Image Manager — ছবি' }),
      demoNote('এখানে কোনো সত্যিকারের ছবি লোড হয় না; ঘরগুলো শুধু জায়গা-চিহ্ন।')
    ].concat(D.images.map(function (im) {
      var st = IMG[im.status];
      return h('div', { class: 'pd-card' }, [
        h('div', { class: 'pd-img', text: 'ছবির জায়গা (নমুনা)' }),
        h('div', { class: 'pd-row' }, [badge(st[0], st[1]), h('span', { class: 'pd-meta', text: im.id + ' • খবর ' + im.story })]),
        h('div', { class: 'pd-meta', text: 'উৎস: ' + im.source }), h('div', { class: 'pd-meta', text: 'স্বত্ব: ' + im.rights }),
        h('div', { class: 'pd-meta', text: 'যাচাই: ' + im.check }),
        h('div', { text: im.alt ? 'Alt: ' + im.alt : 'Alt: — (ম্যানুয়াল ছবি বাছাই দরকার)' })
      ]);
    })));
  }

  /* ---------- RSS Feeds ---------- */
  function feeds() {
    return h('div', null, [
      h('h2', { text: 'RSS Feeds' }),
      demoNote('URL গুলো example.com-এর কাল্পনিক ঠিকানা। ফিড সম্পাদনা পরে কনফিগ ফাইলে (পুল রিকুয়েস্টে) হবে।')
    ].concat(D.feeds.map(function (f) {
      var bad = /ত্রুটি/.test(f.last);
      return h('div', { class: 'pd-card' }, [
        h('div', { class: 'pd-row' }, [badge(f.enabled ? 'চালু' : 'বন্ধ', f.enabled ? 'pd-b-ok' : ''), badge(f.region), badge(f.last, bad ? 'pd-b-bad' : 'pd-b-info')]),
        h('strong', { text: f.name }), h('div', { class: 'pd-meta', text: f.url + ' • শেষ পরীক্ষা ' + f.checked })
      ]);
    })));
  }

  /* ---------- Run History ---------- */
  function runs() {
    return h('div', null, [h('h2', { text: 'Run History' }), demoNote('রান আইডি ও সংখ্যা নমুনা।')].concat(D.runs.map(function (r) {
      return h('div', { class: 'pd-card' }, [
        h('div', { class: 'pd-row' }, [badge(r.status === 'ok' ? 'সফল' : 'ব্যর্থ', r.status === 'ok' ? 'pd-b-ok' : 'pd-b-bad'), badge(r.mode), h('strong', { text: r.id })]),
        h('div', { class: 'pd-meta', text: r.start + ' → ' + r.end }),
        h('div', { text: 'সংগৃহীত ' + r.collected + ' • ডুপ্লিকেট ' + r.dups + ' • প্রতিবেদন ' + r.generated + ' • ড্রাফট ' + r.drafts })
      ]);
    })));
  }

  /* ---------- Errors ---------- */
  function errors() {
    return h('div', null, [h('h2', { text: 'Error Monitoring' }), demoNote('ত্রুটির বার্তা নমুনা। আসল লগে কোনো secret থাকবে না।')].concat(D.errors.map(function (e) {
      return h('details', null, [
        h('summary', { text: e.cat + ' (' + e.count + ') — ' + e.code }),
        h('p', { class: 'pd-meta', text: e.msg }),
        h('strong', { text: 'সমাধান:' }),
        h('ul', null, e.fix.map(function (x) { return h('li', { text: x }); }))
      ]);
    })));
  }

  var SECTIONS = [
    ['overview', 'Overview', overview], ['queue', 'News Queue', queue], ['writer', 'AI Writer', writer], ['seo', 'SEO', seo],
    ['images', 'Images', images], ['feeds', 'RSS Feeds', feeds], ['runs', 'Run History', runs], ['errors', 'Errors', errors]
  ];
  var current = 'overview';
  var tabs = h('div', { class: 'pd-tabs', role: 'tablist' });
  var main = h('div', { class: 'pd-main' });

  function show(id) {
    current = id;
    Array.prototype.forEach.call(tabs.children, function (b) { b.setAttribute('aria-selected', String(b.getAttribute('data-id') === id)); });
    main.textContent = '';
    SECTIONS.forEach(function (s) { if (s[0] === id) { main.appendChild(s[2]()); } });
    window.scrollTo(0, 0);
  }
  SECTIONS.forEach(function (s) {
    tabs.appendChild(h('button', { class: 'pd-tab', type: 'button', role: 'tab', 'data-id': s[0], text: s[1], onclick: function () { show(s[0]); } }));
  });

  root.textContent = '';
  root.appendChild(h('div', { class: 'pd-demo', text: 'DEMO DATA — এটি নমুনা, লাইভ তথ্য নয়' }));
  root.appendChild(h('div', { class: 'pd-head' }, [h('h1', { text: 'পদ্ম বাংলা নিউজ — AI Manager' }), h('p', { text: 'প্রোটোটাইপ v0.1 • শুধু দেখার জন্য • সব লেখা শুধু ড্রাফট' })]));
  root.appendChild(tabs); root.appendChild(main);
  root.appendChild(h('div', { class: 'pd-foot', text: 'কোনো API key/টোকেন এই পাতায় নেই। Secret শুধু GitHub Actions Secrets-এ থাকবে।' }));
  show(current);
})();
