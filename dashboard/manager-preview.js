/* Stage J UI adapter preview. Mock-only: no network, no storage, no approval or publishing. */
(function () {
  'use strict';
  var root = document.getElementById('padma-dash');
  if (!root) return;
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function badge(text, cls) { return el('span', 'pd-badge ' + (cls || ''), text); }
  var snapshot = {
    mode: 'mock-dashboard-preview',
    read_only: true,
    published: false,
    pipeline_status: {state:'mock', last_run:'—', message:'Mock data only; backend not connected'},
    drafts: [
      {id:'mock-001',title:'নমুনা খবর: কলকাতায় নতুন প্রকল্পের ঘোষণা',summary:'এটি শুধু UI পরীক্ষা করার জন্য কাল্পনিক সারাংশ।',source_url:'https://example.org/mock-news-1',review_status:'pending_review',quality_status:'ready_for_editor_review',quality_passed:true,quality_errors:[],quality_warnings:['human_fact_check_required'],published:false},
      {id:'mock-002',title:'নমুনা খবর: শিক্ষাক্ষেত্রে নতুন বিজ্ঞপ্তি',summary:'এটি কাল্পনিক লেখা; বাস্তব খবর নয়।',source_url:'https://example.org/mock-news-2',review_status:'pending_review',quality_status:'needs_revision',quality_passed:false,quality_errors:['body_too_short'],quality_warnings:['human_fact_check_required'],published:false}
    ]
  };
  root.appendChild(el('div','pd-demo','MOCK MODE — লাইভ ডেটা নয়'));
  root.appendChild(el('header','pd-head',''));
  root.lastChild.appendChild(el('h1','', 'পদ্ম বাংলা নিউজ — Manager Preview'));
  root.lastChild.appendChild(el('p','', 'Stage J • শুধু নমুনা UI • কোনো Live Connection নেই'));
  var main=el('main','pd-main');
  root.appendChild(main);
  var notice=el('div','pd-note pd-warn','নিরাপত্তা: এটি শুধু কাল্পনিক নমুনা। Approve/Publish বোতাম নেই; কোনো API বা storage ব্যবহার হচ্ছে না।');
  main.appendChild(notice);
  var stats=el('div','pd-grid');
  [
    ['মোট Draft',snapshot.drafts.length],
    ['পর্যালোচনা বাকি',snapshot.drafts.filter(function(d){return d.review_status==='pending_review';}).length],
    ['Quality Pass',snapshot.drafts.filter(function(d){return d.quality_passed;}).length],
    ['Publish',0]
  ].forEach(function(item){
    var card=el('div','pd-metric');card.appendChild(el('b','',String(item[1])));card.appendChild(el('span','',item[0]));stats.appendChild(card);
  });
  main.appendChild(stats);
  main.appendChild(el('h2','', 'Draft Review — নমুনা তালিকা'));
  snapshot.drafts.forEach(function(draft){
    var card=el('section','pd-card');
    var row=el('div','pd-row');
    row.appendChild(badge(draft.quality_passed?'Quality Pass':'সংশোধন দরকার',draft.quality_passed?'pd-b-ok':'pd-b-bad'));
    row.appendChild(badge(draft.review_status==='pending_review'?'পর্যালোচনা বাকি':'পর্যালোচিত','pd-b-wait'));
    card.appendChild(row);
    card.appendChild(el('h3','',draft.title));
    card.appendChild(el('p','',draft.summary));
    var link=el('a','pd-meta',draft.source_url);
    link.href=draft.source_url;link.target='_blank';link.rel='noopener noreferrer';
    card.appendChild(link);
    if(draft.quality_errors.length){
      card.appendChild(el('p','pd-meta','ত্রুটি: '+draft.quality_errors.join(', ')));
    }
    if(draft.quality_warnings.length){
      card.appendChild(el('p','pd-meta','সতর্কতা: '+draft.quality_warnings.join(', ')));
    }
    card.appendChild(el('p','pd-meta','ID: '+draft.id+' • Publish: বন্ধ'));
    main.appendChild(card);
  });
  root.appendChild(el('footer','pd-foot','Read-only mock preview • Backend/Auth/Live data এখনো সংযুক্ত নয়।'));
})();
