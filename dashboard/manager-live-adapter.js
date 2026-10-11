/* Stage L4: opt-in read-only same-origin API adapter. Token is memory-only. */
(function () {
  'use strict';
  var root = document.getElementById('padma-live-dash');
  if (!root) return;
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function button(text, fn) {
    var b = el('button', 'pd-button', text);
    b.type = 'button';
    b.addEventListener('click', fn);
    return b;
  }
  var token = '';
  var status = el('p', 'pd-note', 'API-তে এখনও সংযোগ করা হয়নি।');
  root.appendChild(el('div', 'pd-demo', 'READ-ONLY MODE — কোনও Publish বা Run action নেই'));
  var header = el('header', 'pd-head');
  header.appendChild(el('h1', '', 'পদ্ম বাংলা নিউজ — Live API Adapter'));
  header.appendChild(el('p', '', 'Stage L4 • একই-origin authenticated API-এর জন্য প্রস্তুত UI'));
  root.appendChild(header);
  var main = el('main', 'pd-main');
  root.appendChild(main);
  main.appendChild(el('div', 'pd-note pd-warn',
    'নিরাপত্তা: এটি কেবল GET /api/dashboard ব্যবহার করে। Token শুধু এই পেজ খোলা থাকা অবস্থায় memory-তে থাকবে; কখনও URL, localStorage বা source code-এ রাখা হবে না।'));
  var form = el('section', 'pd-card');
  form.appendChild(el('h2', '', 'Read-only API সংযোগ'));
  var input = el('input', 'pd-token');
  input.type = 'password';
  input.autocomplete = 'off';
  input.placeholder = 'Dashboard Bearer Token';
  input.setAttribute('aria-label', 'Dashboard Bearer Token');
  form.appendChild(input);
  form.appendChild(button('Connect / Refresh', connect));
  form.appendChild(button('Disconnect', disconnect));
  form.appendChild(status);
  main.appendChild(form);
  var view = el('div', 'pd-live-results');
  main.appendChild(view);

  function disconnect() {
    token = '';
    input.value = '';
    view.replaceChildren();
    status.textContent = 'সংযোগ বিচ্ছিন্ন। Token মুছে ফেলা হয়েছে।';
  }
  function connect() {
    token = input.value.trim();
    if (!token) {
      status.textContent = 'আগে API token লিখতে হবে।';
      return;
    }
    status.textContent = 'একই-origin /api/dashboard থেকে read-only ডেটা আনা হচ্ছে…';
    view.replaceChildren();
    fetch('/api/dashboard', {
      method: 'GET',
      headers: {'Authorization': 'Bearer ' + token, 'Accept': 'application/json'},
      credentials: 'same-origin',
      cache: 'no-store'
    }).then(function (response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    }).then(render).catch(function (error) {
      status.textContent = 'সংযোগ হয়নি: ' + error.message +
        '। API-টি একই origin-এ reverse proxy/host করা আছে কি না যাচাই করো।';
    });
  }
  function render(data) {
    status.textContent = 'API সংযুক্ত হয়েছে • Read-only • Publish বন্ধ';
    var stats = el('div', 'pd-grid');
    [
      ['মোট Draft', data.draft_count || 0],
      ['Review বাকি', data.pending_review_count || 0],
      ['Quality Pass', data.quality_passed_count || 0],
      ['Publish', 0]
    ].forEach(function (item) {
      var card = el('div', 'pd-metric');
      card.appendChild(el('b', '', String(item[1])));
      card.appendChild(el('span', '', item[0]));
      stats.appendChild(card);
    });
    view.appendChild(stats);
    view.appendChild(el('h2', '', 'Draft তালিকা'));
    (data.drafts || []).forEach(function (draft) {
      var card = el('section', 'pd-card');
      card.appendChild(el('h3', '', draft.title || '(শিরোনাম নেই)'));
      card.appendChild(el('p', '', draft.summary || 'সারাংশ নেই'));
      card.appendChild(el('p', 'pd-meta', 'Review: ' + (draft.review_status || 'pending_review')));
      card.appendChild(el('p', 'pd-meta', 'Quality: ' + (draft.quality_status || 'unknown')));
      if (draft.source_url) {
        var link = el('a', 'pd-meta', draft.source_url);
        link.href = draft.source_url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        card.appendChild(link);
      }
      (draft.quality_errors || []).forEach(function (error) {
        card.appendChild(el('p', 'pd-meta', 'ত্রুটি: ' + error));
      });
      (draft.quality_warnings || []).forEach(function (warning) {
        card.appendChild(el('p', 'pd-meta', 'সতর্কতা: ' + warning));
      });
      view.appendChild(card);
    });
    if (!(data.drafts || []).length) view.appendChild(el('p', 'pd-note', 'এখনও কোনও Draft নেই।'));
  }
})();
