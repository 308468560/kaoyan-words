# -*- coding: utf-8 -*-
"""
build_pages.py v2
Build List01.html - List20.html + index.html
Sources per list:
  passages/ListNN.json       - English essays with [[word]] markers
  passages/ListNN_skel.json  - sentences split per paragraph
  passages/ListNN_zh.json    - zh translations + grammar cards + extra glossary
  words.json                 - list vocabulary (phon + cn)
"""
import json, re, os, html

ROOT = r'd:\2\WEB'
PASS = os.path.join(ROOT, 'passages')
MARK = re.compile(r'\[\[([^\[\]]+?)\]\]')
TOKEN = re.compile(r"[A-Za-zÀ-ɏ]+(?:['’\-‑][A-Za-zÀ-ɏ]+)*")

words_data = json.load(open(os.path.join(ROOT, 'words.json'), encoding='utf-8'))
common_dict = json.load(open(os.path.join(PASS, 'common_dict.json'), encoding='utf-8'))
roots_map = json.load(open(os.path.join(PASS, 'roots_map.json'), encoding='utf-8'))

def lookup_root(low):
    for cand in lemma_candidates(low):
        if cand in roots_map:
            return roots_map[cand]
    return None

# ---------------------------------------------------------------- CSS
CSS = r"""
*{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif;background:#f4f6f8;color:#222;line-height:1.6;--artfs:17px;}
#progressBar{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,#2b7cdd,#56a3f0);width:0;z-index:1500;transition:width .12s;}
.wrap{max-width:1250px;margin:0 auto;padding:18px 20px 60px;}
.topbar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:12px;}
.topbar h1{font-size:22px;color:#1f3a5f;}
.topbar h1 small{font-size:13px;color:#7a8799;font-weight:normal;margin-left:10px;}
.nav-links a{display:inline-block;margin-left:8px;padding:6px 14px;border-radius:18px;background:#fff;border:1px solid #d7dee8;color:#2b5797;text-decoration:none;font-size:13px;}
.nav-links a:hover{background:#2b7cdd;color:#fff;border-color:#2b7cdd;}
.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:10px;background:#fff;border-radius:12px;padding:10px 14px;margin-bottom:14px;box-shadow:0 2px 10px rgba(31,58,95,.06);}
.toolbar .grp{display:flex;align-items:center;gap:4px;}
.toolbar .lab{font-size:12px;color:#8a96a5;margin-right:2px;}
.seg{display:inline-flex;border:1px solid #d7dee8;border-radius:18px;overflow:hidden;}
.seg button{border:none;background:#fff;padding:6px 14px;font-size:13px;color:#456;cursor:pointer;}
.seg button.on{background:#2b7cdd;color:#fff;}
.tbtn{border:1px solid #d7dee8;background:#fff;border-radius:18px;padding:6px 13px;font-size:13px;color:#456;cursor:pointer;}
.tbtn:hover{border-color:#2b7cdd;color:#2b7cdd;}
.tbtn.on{background:#fff5e6;border-color:#e6a23c;color:#c87f10;}
.tbtn .n{display:inline-block;background:#e6a23c;color:#fff;border-radius:10px;font-size:11px;padding:0 6px;margin-left:3px;}
.tbtn.on .n{background:#e6a23c;}
.meta-bar{background:#eef4fc;border:1px solid #d4e4f7;border-radius:10px;padding:9px 16px;font-size:13px;color:#456;margin-bottom:16px;}
.meta-bar b{color:#2b5797;}
.legend-dots{display:inline-flex;gap:14px;margin-left:6px;flex-wrap:wrap;}
.legend-dots i{font-style:normal;}
.dot-l{color:#2b7cdd;font-weight:bold;border-bottom:1px dashed #2b7cdd;}
.dot-e{color:#1c9e63;font-weight:bold;border-bottom:1px dashed #1c9e63;}
.article{background:#fff;border-radius:14px;box-shadow:0 4px 18px rgba(31,58,95,.08);padding:32px 40px;font-size:var(--artfs);}
.para{margin:0 0 22px;}
.sent{position:relative;display:block;margin-bottom:12px;padding-left:26px;}
.en-zone{line-height:2.15;text-align:justify;color:#2b2b2b;}
.zh{display:none;font-size:.92em;color:#556;line-height:1.9;background:#f4f8ff;border-left:3px solid #b9d4f5;padding:7px 12px;margin-top:5px;border-radius:0 8px 8px 0;}
/* EN immersion mode: hover sentence -> zh bubble; .pinned -> inline */
body.mode-en .sent:hover .zh{display:block;position:absolute;z-index:400;max-width:420px;left:26px;top:100%;background:#263445;color:#eaf1fb;border-left:3px solid #6aa3e0;padding:9px 13px;border-radius:8px;box-shadow:0 10px 26px rgba(0,0,0,.25);}
body.mode-en .sent.pinned .zh{display:block;position:static;max-width:none;background:#f4f8ff;color:#556;border-left:3px solid #b9d4f5;padding:7px 12px;}
body.mode-bi .zh{display:block;}
body.mode-zh .en-zone{display:none;}
body.mode-zh .zh{display:block;background:transparent;border-left:none;padding:7px 0 0;color:#333;font-size:1em;}
body.mode-zh .sent{padding-left:0;}
.sent-tools{position:absolute;left:0;top:2px;display:none;gap:2px;}
.sent:hover .sent-tools{display:flex;}
.sent-tools span{cursor:pointer;font-size:13px;line-height:1;padding:2px 3px;border-radius:5px;background:#eef4fc;}
.sent-tools span:hover{background:#dbe8fa;}
.sent-tools .st-gram{display:inline-block;background:#fdf3e0;}
.sent-tools .st-gram:hover{background:#f8e2b4;}
.sent.has-gram .sent-tools .st-gram{display:inline-block;}
.sent.gram-hl{background:linear-gradient(90deg,#fff7e6,transparent 60%);border-radius:8px;}
.sent.gram-hl .en-zone{box-shadow:inset 3px 0 #e6a23c;padding-left:8px;border-radius:3px;}
/* word styles */
.vocab-word{color:#2b7cdd;font-weight:bold;border-bottom:1px dashed #2b7cdd;cursor:pointer;position:relative;}
.extra-word{color:#1c9e63;border-bottom:1px dashed #1c9e63;cursor:pointer;position:relative;}
.plain-word{cursor:pointer;position:relative;border-bottom:1px dotted rgba(0,0,0,.18);}
.plain-word:hover{background:#f2f6fc;}
.vocab-word:hover,.extra-word:hover{background:#eaf3ff;}
.extra-word:hover{background:#e9f8f1;}
.vocab-word.saved{color:#d9534f;border-bottom-color:#d9534f;}
.vocab-word.saved:hover{background:#fdeeec;}
.pinned-tip .tip{display:block !important;}
.tip{display:none;position:absolute;left:0;top:100%;background:#2b2b2b;color:#f5f5f5;padding:12px 14px;border-radius:10px;font-size:13px;line-height:1.65;min-width:250px;max-width:340px;white-space:pre-wrap;z-index:1000;box-shadow:0 8px 26px rgba(0,0,0,.28);font-weight:normal;text-align:left;margin-top:8px;}
.tip::before{content:"";position:absolute;top:-6px;left:20px;border-width:0 6px 6px;border-style:solid;border-color:transparent transparent #2b2b2b;}
.tip::after{content:"";position:absolute;top:-8px;left:0;right:0;height:8px;}
.vocab-word:hover .tip,.extra-word:hover .tip,.plain-word:hover .tip{display:block;}
.tip .troot{display:block;margin-top:7px;padding-top:7px;border-top:1px dashed #555;color:#8de0b4;font-size:12.5px;line-height:1.55;}
sup.rb{font-size:10px;color:#fff;background:#1c9e63;border-radius:4px;padding:0 3px;margin-left:2px;vertical-align:super;font-weight:normal;font-family:Arial;}
.vocab-word.rooted{border-bottom-color:#1c9e63;}
body.root-only .vocab-word:not(.rooted),
body.root-only .extra-word,
body.root-only .plain-word{opacity:.16;}
body.root-only sup.rb{display:inline-block;}
.tip .tw{font-weight:bold;font-size:14.5px;color:#ffd98a;}
.tip .tp{color:#b9d8ff;}
.tip .tc{margin-top:2px;}
.tip .thint{display:block;margin-top:7px;font-size:11.5px;color:#9aa6b2;}
.tip .tacts{display:flex;gap:8px;margin-top:8px;}
.tip .tacts a,.tip .tacts span{font-size:12px;background:#444;padding:3px 9px;border-radius:10px;color:#eee;text-decoration:none;cursor:pointer;}
.tip .tacts a:hover,.tip .tacts span:hover{background:#5a5a5a;}
/* grammar card */
.gram-card{display:none;background:#fffdf5;border:1px solid #f0dfa8;border-radius:10px;padding:14px 18px;margin:6px 0 14px 26px;box-shadow:0 3px 12px rgba(160,130,40,.1);}
.gram-card.open{display:block;}
.gram-card h4{font-size:14.5px;color:#a9761a;margin-bottom:3px;}
.gram-card .skel{font-size:12.5px;color:#8a7a4e;margin-bottom:9px;}
.gram-card .gsent{font-size:13.5px;line-height:2;color:#333;background:#fff;border:1px dashed #ecd9a3;border-radius:8px;padding:9px 12px;margin-bottom:10px;}
.gram-card mark.gh{background:transparent;border-radius:3px;padding:0 2px;}
.gram-card mark.gh[data-n]::after{content:attr(data-n);font-size:10px;vertical-align:super;color:#fff;background:#e6a23c;border-radius:50%;padding:0 4px;margin-left:1px;font-weight:bold;}
.gram-card mark.gh.g1{background:#ffe9c2;} .gram-card mark.gh.g2{background:#d8ecff;}
.gram-card mark.gh.g3{background:#ddf5e2;} .gram-card mark.gh.g4{background:#f5dcf5;}
.gram-card mark.gh.g5{background:#ffe0d6;} .gram-card mark.gh.g6{background:#e4e0fb;}
.gram-card table{width:100%;border-collapse:collapse;font-size:12.5px;margin-bottom:9px;}
.gram-card td{border-top:1px solid #f0e6c8;padding:5px 7px;vertical-align:top;color:#444;}
.gram-card td.role{width:104px;color:#a9761a;font-weight:bold;white-space:nowrap;}
.gram-card td.role b{display:inline-block;background:#e6a23c;color:#fff;border-radius:50%;width:16px;height:16px;line-height:16px;text-align:center;font-size:10px;margin-right:5px;}
.gram-card td.frag{color:#2b5797;width:46%;}
.gram-card .pts{font-size:12.5px;color:#555;}
.gram-card .pts li{margin-left:18px;margin-bottom:3px;}
.gram-card .gzh{font-size:12.5px;color:#6a7a8a;margin-top:8px;border-top:1px dashed #ecd9a3;padding-top:7px;}
.gram-card .gacts{margin-top:8px;}
.gram-card .gacts span{cursor:pointer;font-size:12px;background:#fdf0d3;border:1px solid #e6c87a;color:#8a6d2b;padding:3px 11px;border-radius:10px;}
.gram-card .gacts span:hover{background:#f8e2ac;}
/* vocab panel */
#vocabPanel{position:fixed;right:16px;top:84px;width:296px;max-height:calc(100vh - 104px);overflow:auto;background:#fffbeb;border:1px solid #ecd9a3;border-radius:14px;box-shadow:0 8px 28px rgba(90,70,20,.18);padding:14px 16px;z-index:500;}
#vocabPanel h3{font-size:15px;color:#8a6d2b;margin-bottom:6px;}
#vocabPanel .sub{font-size:12px;color:#a08a4e;margin-bottom:10px;}
#panelEmpty{font-size:13px;color:#b3a272;padding:4px 0 10px;}
.chip{display:inline-flex;align-items:center;gap:5px;background:#fff;border:1px solid #e3cd84;border-radius:16px;padding:3px 6px 3px 11px;margin:0 6px 8px 0;font-size:13px;}
.chip .cw{color:#b3541e;font-weight:bold;cursor:help;}
.chip .cs{cursor:pointer;color:#b3964a;padding:0 2px;}
.chip .cs:hover{color:#2b7cdd;}
.chip .del{cursor:pointer;color:#a0813c;font-weight:bold;padding:0 5px;border-radius:50%;}
.chip .del:hover{background:#f5e6c0;color:#7a5a10;}
.panel-btns{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;}
.panel-btns button{flex:1;min-width:78px;padding:7px 6px;border:none;border-radius:8px;cursor:pointer;font-size:12.5px;color:#fff;}
#btnClear{background:#e08b6f;} #btnClear:hover{background:#cf6f4f;}
#btnCopy{background:#c9a94f;} #btnCopy:hover{background:#b1912f;}
#btnReview{background:#7a67d8;} #btnReview:hover{background:#6552c4;}
#toast{position:fixed;left:50%;bottom:34px;transform:translateX(-50%);background:#333;color:#fff;padding:10px 22px;border-radius:22px;font-size:13.5px;opacity:0;transition:opacity .25s;z-index:2000;pointer-events:none;}
#toast.show{opacity:.94;}
/* flashcard review overlay */
#reviewMask{display:none;position:fixed;inset:0;background:rgba(20,30,45,.62);z-index:3000;align-items:center;justify-content:center;padding:20px;}
#reviewMask.open{display:flex;}
.rcard{background:#fff;border-radius:18px;width:min(520px,92vw);padding:30px 30px 24px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.35);}
.rcard .rprog{font-size:12.5px;color:#8a96a5;margin-bottom:14px;}
.rflip{position:relative;min-height:170px;perspective:1000px;cursor:pointer;margin-bottom:16px;}
.rinner{position:relative;width:100%;min-height:170px;transition:transform .35s;transform-style:preserve-3d;}
.rflip.flipped .rinner{transform:rotateX(180deg);}
.rface{position:absolute;inset:0;backface-visibility:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;border-radius:14px;padding:18px;}
.rfront{background:#f3f7ff;border:1px solid #d4e4f7;}
.rfront .rw{font-size:34px;font-weight:bold;color:#2b5797;}
.rfront .rph{color:#5a83b8;font-size:15px;}
.rfront .rsp{cursor:pointer;font-size:18px;}
.rback{background:#fff8ec;border:1px solid #ecd9a3;transform:rotateX(180deg);font-size:16px;color:#6b5420;line-height:1.8;}
.rtip{font-size:12px;color:#a0b0c0;}
.rbtns{display:flex;gap:12px;justify-content:center;}
.rbtns button{border:none;border-radius:22px;padding:10px 26px;font-size:14px;cursor:pointer;color:#fff;}
#rKeep{background:#e6a23c;} #rKeep:hover{background:#cf8a1c;}
#rKnown{background:#37b37c;} #rKnown:hover{background:#2c9866;}
#rClose{position:absolute;top:14px;right:18px;border:none;background:none;font-size:22px;color:#8a96a5;cursor:pointer;}
.rdone{font-size:16px;color:#2c9866;line-height:2;}
/* index */
.hero{text-align:center;padding:24px 10px 6px;}
.hero h1{font-size:29px;color:#1f3a5f;margin-bottom:9px;}
.hero p{color:#5f6f82;font-size:14.5px;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(284px,1fr));gap:16px;margin-top:22px;}
.card{display:block;background:#fff;border-radius:14px;padding:19px 21px;text-decoration:none;color:inherit;box-shadow:0 4px 16px rgba(31,58,95,.07);border-top:4px solid #2b7cdd;transition:transform .12s,box-shadow .12s;position:relative;}
.card:hover{transform:translateY(-3px);box-shadow:0 10px 26px rgba(43,124,221,.18);}
.card h2{font-size:18px;color:#1f3a5f;margin-bottom:6px;}
.card .tag{display:inline-block;font-size:12px;background:#eef4fc;color:#2b5797;border-radius:10px;padding:2px 10px;margin-bottom:9px;}
.card .nums{font-size:12.5px;color:#7a8799;margin-bottom:7px;}
.card .pwrap{height:5px;background:#eef1f5;border-radius:4px;overflow:hidden;margin-top:9px;}
.card .pbar{height:100%;width:0;background:linear-gradient(90deg,#2b7cdd,#56a3f0);}
.card.done::after{content:"✓ 已读完";position:absolute;top:14px;right:14px;font-size:11.5px;color:#fff;background:#37b37c;border-radius:10px;padding:2px 9px;}
.card .pct{font-size:11.5px;color:#9aa8b8;margin-top:4px;text-align:right;}
.legend{margin-top:24px;background:#fff;border-radius:12px;padding:16px 22px;font-size:13px;color:#5a6a7d;box-shadow:0 2px 10px rgba(31,58,95,.06);line-height:2;}
.legend .dot-l,.legend .dot-e{font-weight:bold;}
@media (max-width:1200px){
  #vocabPanel{left:0;right:0;top:auto;bottom:0;width:100%;max-height:40vh;border-radius:14px 14px 0 0;}
  .wrap{padding-bottom:44vh;}
  .article{padding:22px 18px;}
  body.mode-en .sent:hover .zh{position:static;background:#f4f8ff;color:#556;border-left:3px solid #b9d4f5;max-width:none;}
}
"""

# ---------------------------------------------------------------- JS
JS = r"""
const QUEUE_KEY='ky_vocab_queue_v2', PREFS_KEY='ky_prefs_v2';
let queue=[];
try{queue=JSON.parse(localStorage.getItem(QUEUE_KEY)||'[]');}catch(e){queue=[];}
let prefs={mode:'bi',fs:17,accent:'en-US',gramHL:false,rootOnly:false};
try{Object.assign(prefs,JSON.parse(localStorage.getItem(PREFS_KEY)||'{}'));}catch(e){}
const LIST_N = parseInt(document.body.dataset.list||'0',10);
const READ_KEY='ky_read_'+String(LIST_N).padStart(2,'0');
function saveQueue(){localStorage.setItem(QUEUE_KEY,JSON.stringify(queue));}
function savePrefs(){localStorage.setItem(PREFS_KEY,JSON.stringify(prefs));}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
let toastTm;
function showToast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');clearTimeout(toastTm);toastTm=setTimeout(()=>t.classList.remove('show'),1500);}
/* ---------- text to speech ---------- */
let voices=[];
function loadVoices(){voices=speechSynthesis.getVoices()||[];}
if('speechSynthesis' in window){loadVoices();speechSynthesis.onvoiceschanged=loadVoices;}
let _utter=null,_spkTm=null;
function speak(text){
  if(!('speechSynthesis' in window)){showToast('当前浏览器不支持朗读');return;}
  speechSynthesis.cancel();
  if(_spkTm)clearTimeout(_spkTm);
  _spkTm=setTimeout(function(){
    const u=new SpeechSynthesisUtterance(text);
    _utter=u;
    u.lang=prefs.accent;u.rate=0.88;
    const want=prefs.accent;
    let v=voices.find(v=>v.lang===want)||voices.find(v=>v.lang.startsWith(want.slice(0,2)));
    if(v){u.voice=v;u.lang=v.lang;}
    u.onend=u.onerror=function(){if(_utter===u)_utter=null;};
    speechSynthesis.speak(u);
  },80);
}
/* ---------- vocab queue ---------- */
function renderPanel(){
  const box=document.getElementById('chipBox');
  document.getElementById('queueCount').textContent=queue.length;
  if(!queue.length){box.innerHTML='<div id="panelEmpty">还没有生词。点击文中<span style="color:#2b7cdd;font-weight:bold">蓝色词表词</span>或<span style="color:#1c9e63;font-weight:bold">绿色拓展词</span>加入。</div>';return;}
  box.innerHTML=queue.map((it,i)=>'<span class="chip"><span class="cs" data-sp="'+i+'" title="朗读">&#128264;</span><span class="cw" title="'+esc(it.p+' '+it.c)+'">'+esc(it.w)+'</span><span class="del" data-i="'+i+'">&#10005;</span></span>').join('');
}
function savedSet(){const s={};queue.forEach(it=>s[it.w.toLowerCase()]=1);return s;}
function syncWordState(){
  const have=savedSet();
  document.querySelectorAll('.vocab-word').forEach(s=>s.classList.toggle('saved',!!have[s.dataset.word.toLowerCase()]));
}
function addWord(w,p,c){
  if(queue.some(it=>it.w.toLowerCase()===w.toLowerCase())){showToast('已在生词本：'+w);return;}
  queue.push({w,p,c});saveQueue();renderPanel();syncWordState();showToast('已加入生词本：'+w);
}
function delWord(w){
  queue=queue.filter(it=>it.w.toLowerCase()!==w.toLowerCase());saveQueue();renderPanel();syncWordState();
}
document.addEventListener('click',function(e){
  const sp=e.target.closest('.chip .cs');
  if(sp){speak(queue[parseInt(sp.dataset.sp,10)].w);return;}
  const del=e.target.closest('.chip .del');
  if(del){delWord(queue[parseInt(del.dataset.i,10)].w);return;}
  const tact=e.target.closest('.tacts .tts');
  if(tact){speak(tact.dataset.tts);return;}
  const gsp=e.target.closest('.gacts .gtts');
  if(gsp){speak(gsp.dataset.tts);return;}
  const w=e.target.closest('.vocab-word,.extra-word');
  if(w){
    const word=w.dataset.word;
    if(w.classList.contains('saved')){delWord(word);showToast('已从生词本移除：'+word);}
    else addWord(word,w.dataset.phon||'',w.dataset.cn||'');
    document.querySelectorAll('.pinned-tip').forEach(x=>{if(x!==w)x.classList.remove('pinned-tip');});
    w.classList.add('pinned-tip');
    setTimeout(()=>w.classList.remove('pinned-tip'),2600);
    return;
 }
  // sentence tools
  const stts=e.target.closest('.st-tts');
  if(stts){speak(stts.closest('.sent').dataset.en);return;}
  const szh=e.target.closest('.st-zh');
  if(szh){szh.closest('.sent').classList.toggle('pinned');return;}
  const sgr=e.target.closest('.st-gram');
  if(sgr){
    const s=sgr.closest('.sent');
    const card=document.getElementById('card-'+s.dataset.pid+'-'+s.dataset.sid);
    if(card)card.classList.toggle('open');
    return;
  }
  document.querySelectorAll('.pinned-tip').forEach(x=>x.classList.remove('pinned-tip'));
});
document.getElementById('btnClear').addEventListener('click',function(){
  if(!queue.length)return;
  if(confirm('确定清空全部生词吗？')){queue=[];saveQueue();renderPanel();syncWordState();}
});
document.getElementById('btnCopy').addEventListener('click',function(){
  if(!queue.length){showToast('生词本是空的');return;}
  const txt=queue.map(it=>it.w+'  '+it.p+'  '+it.c).join('\n');
  const done=()=>showToast('已复制 '+queue.length+' 个生词');
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(done).catch(fb);}else fb();
  function fb(){const ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');done();}catch(x){showToast('复制失败');}document.body.removeChild(ta);}
});
/* ---------- reading modes / prefs ---------- */
function applyPrefs(){
  document.body.classList.remove('mode-en','mode-bi','mode-zh');
  document.body.classList.add('mode-'+prefs.mode);
  document.querySelectorAll('.seg.modes button').forEach(b=>b.classList.toggle('on',b.dataset.mode===prefs.mode));
  document.documentElement.style.setProperty('--artfs',prefs.fs+'px');
  document.getElementById('accentBtn').textContent=prefs.accent==='en-GB'?'🇬🇧 英音':'🇺🇸 美音';
  document.body.classList.toggle('gram-all',prefs.gramHL);
  document.getElementById('gramBtn').classList.toggle('on',prefs.gramHL);
  document.querySelectorAll('.gram-card').forEach(c=>c.classList.toggle('open',prefs.gramHL));
  document.querySelectorAll('.sent.has-gram').forEach(s=>s.classList.toggle('gram-hl',prefs.gramHL));
  document.body.classList.toggle('root-only',prefs.rootOnly);
  document.getElementById('rootBtn').classList.toggle('on',prefs.rootOnly);
}
document.querySelectorAll('.seg.modes button').forEach(b=>b.addEventListener('click',()=>{prefs.mode=b.dataset.mode;savePrefs();applyPrefs();}));
document.getElementById('fsMinus').addEventListener('click',()=>{prefs.fs=Math.max(14,prefs.fs-1);savePrefs();applyPrefs();});
document.getElementById('fsPlus').addEventListener('click',()=>{prefs.fs=Math.min(23,prefs.fs+1);savePrefs();applyPrefs();});
document.getElementById('accentBtn').addEventListener('click',()=>{prefs.accent=prefs.accent==='en-US'?'en-GB':'en-US';savePrefs();applyPrefs();showToast(prefs.accent==='en-GB'?'已切换为英音':'已切换为美音');});
document.getElementById('gramBtn').addEventListener('click',()=>{prefs.gramHL=!prefs.gramHL;savePrefs();applyPrefs();});
document.getElementById('rootBtn').addEventListener('click',()=>{prefs.rootOnly=!prefs.rootOnly;savePrefs();applyPrefs();showToast(prefs.rootOnly?'已聚焦本篇词根词，其余词变淡':'已退出词根聚焦');});
/* ---------- reading progress ---------- */
const bar=document.getElementById('progressBar');
function onScroll(){
  const h=document.documentElement;
  const max=h.scrollHeight-h.clientHeight;
  const p=max>0?Math.min(1,h.scrollTop/max):1;
  bar.style.width=(p*100).toFixed(1)+'%';
  if(p>=0.95){const v=parseFloat(localStorage.getItem(READ_KEY)||'0');if(v<1){localStorage.setItem(READ_KEY,'1');showToast('本篇已读完，进度已保存 ✓');}}
  else{const v=parseFloat(localStorage.getItem(READ_KEY)||'0');if(v<0.95)localStorage.setItem(READ_KEY,p.toFixed(2));}
}
window.addEventListener('scroll',onScroll,{passive:true});
/* ---------- flashcard review ---------- */
const mask=document.getElementById('reviewMask');
let rList=[],rIdx=0;
function openReview(){
  if(!queue.length){showToast('生词本是空的，先去文章里收藏吧');return;}
  rList=queue.slice().sort(()=>Math.random()-0.5);rIdx=0;
  mask.classList.add('open');renderCard();
}
function renderCard(){
  const box=document.getElementById('rBox');
  if(rIdx>=rList.length){
    box.innerHTML='<div class="rdone">🎉 本轮生词已全部过完！<br>坚持复习，记得回来读下一篇短文。</div>';
    return;
  }
  const it=rList[rIdx];
  box.innerHTML='<div class="rprog">第 '+(rIdx+1)+' / '+rList.length+' 张 · 点击卡片翻面看释义</div>'
    +'<div class="rflip" id="rFlip"><div class="rinner">'
    +'<div class="rface rfront"><div class="rw">'+esc(it.w)+'</div><div class="rph">'+esc(it.p||'')+'</div><div class="rsp" data-sp="1">&#128264; 朗读</div></div>'
    +'<div class="rface rback">'+esc(it.c||'')+'</div>'
    +'</div></div><div class="rtip">还不熟 → 留在生词本　｜　已掌握 → 自动移除</div>';
  document.getElementById('rFlip').addEventListener('click',function(ev){if(!ev.target.dataset.sp)this.classList.toggle('flipped');else speak(it.w);});
}
document.getElementById('btnReview').addEventListener('click',openReview);
document.getElementById('rClose').addEventListener('click',()=>{mask.classList.remove('open');speechSynthesis.cancel();renderPanel();syncWordState();});
document.getElementById('rKeep').addEventListener('click',()=>{rIdx++;renderCard();});
document.getElementById('rKnown').addEventListener('click',()=>{
  if(rIdx<rList.length){const w=rList[rIdx].w;queue=queue.filter(it=>it.w!==w);saveQueue();}
  rIdx++;renderCard();
});
/* ---------- init ---------- */
renderPanel();syncWordState();applyPrefs();onScroll();
"""

# ---------------------------------------------------------------- rendering
def norm(s):
    return MARK.sub(lambda m: m.group(1), s)

def lemma_candidates(low):
    c = {low}
    if low.endswith('ies') and len(low) > 4: c.add(low[:-3] + 'y')
    if low.endswith('ied') and len(low) > 4: c.add(low[:-3] + 'y')
    if low.endswith('es') and len(low) > 3: c.add(low[:-2]); c.add(low[:-1])
    if low.endswith('s') and not low.endswith('ss') and len(low) > 3: c.add(low[:-1])
    if low.endswith('ing') and len(low) > 5:
        c.add(low[:-3]); c.add(low[:-3] + 'e')
        if len(low) > 6 and low[-4] == low[-5]: c.add(low[:-4])
    if low.endswith('ed') and len(low) > 4:
        c.add(low[:-2]); c.add(low[:-1])
        if len(low) > 5 and low[-3] == low[-4]: c.add(low[:-3])
    if low.endswith('er') and len(low) > 4: c.add(low[:-2])
    if low.endswith('est') and len(low) > 5: c.add(low[:-3])
    if low.endswith('ly') and len(low) > 3: c.add(low[:-2])
    return c

def make_span(kind, word, display, phon, cn, lemma_note=''):
    cls = {'list': 'vocab-word', 'extra': 'extra-word', 'plain': 'plain-word'}[kind]
    q = lambda s: html.escape(str(s), quote=True)
    if kind == 'plain':
        if cn:
            ph = f' <span class="tp">{q(phon)}</span>' if phon else ''
            tip = ('<span class="tip"><span class="tw">%s</span>%s'
                   '<span class="tc">%s</span>'
                   '<span class="thint">公共词汇 · 不入生词本</span>'
                   '<span class="tacts"><span class="tts" data-tts="%s">&#128264; 朗读</span>'
                   '<a href="https://www.youdao.com/result?word=%s&amp;lang=en" target="_blank" rel="noopener">&#128269; 有道</a>'
                   '</span></span>') % (q(display), ph, q(cn), q(word), q(word))
        else:
            tip = ('<span class="tip"><span class="tw">%s</span>'
                   '<span class="thint">可朗读或跳转词典查询</span>'
                   '<span class="tacts"><span class="tts" data-tts="%s">&#128264; 朗读</span>'
                   '<a href="https://www.youdao.com/result?word=%s&amp;lang=en" target="_blank" rel="noopener">&#128269; 有道</a>'
                   '</span></span>') % (q(display), q(word), q(word))
        return f'<span class="{cls}" data-word="{q(word)}">{html.escape(display)}{tip}</span>'
    note = ('<span class="thint">%s · 点击加入 / 移出生词本</span>' % lemma_note) if lemma_note \
           else '<span class="thint">点击加入 / 移出生词本</span>'
    troot = ''
    sup = ''
    rooted = ''
    if kind == 'list':
        ri = lookup_root(word.lower())
        if ri:
            rooted = ' rooted'
            sup = '<sup class="rb">根</sup>'
            troot = '<span class="troot">&#127793; 词根：%s</span>' % q(ri['br'])
    tip = ('<span class="tip"><span class="tw">%s</span> <span class="tp">%s</span>'
           '<span class="tc">%s</span>%s%s'
           '<span class="tacts"><span class="tts" data-tts="%s">&#128264; 朗读</span>'
           '<a href="https://www.youdao.com/result?word=%s&amp;lang=en" target="_blank" rel="noopener">&#128269; 词典</a>'
           '</span></span>') % (q(word), q(phon), q(cn), troot, note, q(word), q(word))
    return (f'<span class="{cls}{rooted}" data-word="{q(word)}" data-phon="{q(phon)}" '
            f'data-cn="{q(cn)}">{html.escape(display)}{sup}{tip}</span>')

def render_en_segment(seg, list_lookup, extra_lookup, common_lookup):
    """Render a marker-free segment: list words / extra words / phrases / plain."""
    toks = list(TOKEN.finditer(seg))
    out = []
    pos = 0
    i = 0
    while i < len(toks):
        m = toks[i]
        out.append(html.escape(seg[pos:m.start()]))
        low = m.group(0).replace('’', "'").replace('‑', '-').lower()
        # 1) multi-word extra phrase (longest first)
        matched = False
        for L in (3, 2):
            if i + L <= len(toks):
                gap_ok = all(seg[toks[i + k].end():toks[i + k + 1].start()].strip() == ''
                             for k in range(L - 1))
                if gap_ok:
                    words_l = [toks[i + k].group(0).replace('’', "'").replace('‑', '-').lower() for k in range(L)]
                    phrase = ' '.join(words_l)
                    if phrase in extra_lookup:
                        info = extra_lookup[phrase]
                        end = toks[i + L - 1].end()
                        out.append(make_span('extra', phrase, seg[m.start():end], info['phon'], info['def']))
                        pos = end; i += L; matched = True; break
        if matched: continue
        # 2) list word (bare occurrence)
        hit = None
        if low in list_lookup:
            w = list_lookup[low]; hit = ('list', w['word'], w['phon'], w['def'], '')
        if hit is None:
            # 3) extra word with inflection fallback
            for cand in lemma_candidates(low):
                if cand in extra_lookup:
                    info = extra_lookup[cand]
                    note = f'原形 {cand}' if cand != low else ''
                    hit = ('extra', cand, info['phon'], info['def'], note)
                    break
        if hit is None:
            for cand in lemma_candidates(low):
                if cand in list_lookup:
                    w = list_lookup[cand]
                    hit = ('list', w['word'], w['phon'], w['def'], f'原形 {w["word"]}' if cand != low else '')
                    break
        if hit is None:
            # 4) common dict with inflection fallback
            for cand in lemma_candidates(low):
                if cand in common_lookup:
                    info = common_lookup[cand]
                    note = f'原形 {cand}' if cand != low else ''
                    hit = ('plain', cand, info['phon'], info['def'], note)
                    break
        if hit is None:
            out.append(make_span('plain', low, m.group(0), '', ''))
        else:
            kind, w, phon, cn, nnote = hit
            out.append(make_span(kind, w, m.group(0), phon, cn, nnote))
        pos = m.end(); i += 1
    out.append(html.escape(seg[pos:]))
    return ''.join(out)

def render_en_text(text, list_lookup, extra_lookup, common_lookup):
    parts = []
    pos = 0
    for m in MARK.finditer(text):
        parts.append(render_en_segment(text[pos:m.start()], list_lookup, extra_lookup, common_lookup))
        display = m.group(1).strip()
        info = list_lookup.get(display.lower())
        if info is None:
            raise ValueError('marker not in list: ' + display)
        parts.append(make_span('list', info['word'], display, info['phon'], info['def']))
        pos = m.end()
    parts.append(render_en_segment(text[pos:], list_lookup, extra_lookup, common_lookup))
    return ''.join(parts)

def highlight_grammar_sentence(plain_en, parts):
    low = ' '.join(plain_en.split()).lower()
    intervals = []
    for idx, p in enumerate(parts):
        t = ' '.join(norm(str(p.get('text', ''))).split()).lower()
        if not t: continue
        at = low.find(t)
        if at >= 0:
            intervals.append((at, at + len(t), idx))
    intervals.sort(key=lambda x: x[0])
    # flat string positions map back to original whitespace-collapsed text
    flat = ' '.join(plain_en.split())
    out, pos, used = [], 0, -1
    for s, e, idx in intervals:
        if s < pos: continue
        out.append(html.escape(flat[pos:s]))
        out.append(f'<mark class="gh g{(idx % 6) + 1}" data-n="{idx + 1}">{html.escape(flat[s:e])}</mark>')
        pos = e
    out.append(html.escape(flat[pos:]))
    return ''.join(out)

# 跨页复习到期提醒（注入 List页 / roots / index 的 <script> 内，独立运行）
REVIEW_BELL_JS = r"""
/* ---- 复习到期提醒（跨页）：每20秒检查一次，到期在右下角弹出提醒 ---- */
(function(){
  try{
    var IVL=[5*6e4,30*6e4,12*36e5,864e5,2*864e5,4*864e5,7*864e5,15*864e5];
    var hideUntil=0, bell=null, dueShown=-1;
    function tick(){
      var rv;try{rv=JSON.parse(localStorage.getItem('ky_review_v1')||'null');}catch(e){return;}
      if(!rv||!rv.words)return;
      var now=Date.now(),due=0;
      for(var k in rv.words){var st=rv.words[k];if(!st||st.s>=8)continue;
        var t0=(st.t0===undefined?st.t:st.t0);
        var d=(st.s<=1?st.t:t0)+IVL[st.s];
        if(d<=now)due++;}
      if(due>0&&now>=hideUntil)show(due);
      else if(bell&&due===0){bell.remove();bell=null;dueShown=-1;}
    }
    function show(due){
      if(bell&&dueShown===due)return;
      dueShown=due;
      if(!bell){
        bell=document.createElement('div');
        bell.style.cssText='position:fixed;right:18px;bottom:18px;z-index:4000;background:linear-gradient(135deg,#e6a23c,#e0803c);color:#fff;border-radius:14px;padding:12px 16px;box-shadow:0 10px 30px rgba(200,120,20,.45);font-size:13.5px;max-width:300px;line-height:1.6;font-family:inherit;';
        document.body.appendChild(bell);
      }
      var back=encodeURIComponent(location.pathname.split('/').pop()||'index.html');
      bell.innerHTML='<div style="font-weight:bold;margin-bottom:4px">🔔 复习时间到！</div><div>'+due+' 个单词已到达遗忘临界点</div>'
        +'<div style="margin-top:8px;display:flex;gap:8px"><a href="review.html?back='+back+'" style="flex:1;text-align:center;background:#fff;color:#c87f10;text-decoration:none;border-radius:9px;padding:5px 0;font-weight:bold">去复习 →</a>'
        +'<span class="rvBellX" style="cursor:pointer;background:rgba(255,255,255,.25);border-radius:9px;padding:5px 10px">稍后</span></div>';
      var x=bell.querySelector('.rvBellX');
      if(x)x.addEventListener('click',function(){hideUntil=Date.now()+10*6e4;if(bell){bell.remove();bell=null;dueShown=-1;}});
    }
    setInterval(tick,20000);setTimeout(tick,1500);
  }catch(e){}
})();
"""

PAGE_TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body class="mode-bi" data-list="__N__">
<div id="progressBar"></div>
<div class="wrap">
  <div class="topbar">
    <h1>十天搞定考研词汇 · 埋词精读<small>__LISTKEY__</small></h1>
    <div class="nav-links">__NAV__</div>
  </div>
  <div class="toolbar">
    <div class="grp"><span class="lab">阅读模式</span>
      <div class="seg modes">
        <button data-mode="en">英文沉浸</button>
        <button data-mode="bi">逐句对照</button>
        <button data-mode="zh">仅看中文</button>
      </div>
    </div>
    <div class="grp"><span class="lab">字号</span>
      <button class="tbtn" id="fsMinus">A－</button>
      <button class="tbtn" id="fsPlus">A＋</button>
    </div>
    <button class="tbtn" id="accentBtn">🇺🇸 美音</button>
    <button class="tbtn" id="gramBtn">🔷 长难句<span class="n">__NGRAM__</span></button>
    <a class="tbtn" href="roots.html">🌱 词根中心</a>
    <a class="tbtn" href="review.html">📅 每日复习</a>
    <button class="tbtn" id="rootBtn">🌱 只看词根词</button>
  </div>
  <div class="meta-bar">
    <b>List __N__ · Day __DAY__</b> ｜ 词表 <b>__NWORDS__</b> 词 · 句子 <b>__NSENTS__</b> 句 · 拓展词 <b>__NEXTRA__</b> · 长难句 <b>__NGRAM__</b> 句 · 🌱 词根词 <b>__NROOT__</b>
    <span class="legend-dots"><i><span class="dot-l">蓝色</span>＝本 List 词表词</i><i><span class="dot-e">绿色</span>＝超纲拓展词/短语</i><i>带 <sup class="rb">根</sup> 角标＝可用 60 词根拆解</i><i>其余单词也可悬停查词、朗读</i></span>
  </div>
  <div class="article" id="article">__BODY__</div>
</div>
<div id="vocabPanel">
  <h3>📓 不熟悉生词队列</h3>
  <div class="sub">共 <b id="queueCount">0</b> 个 · 跨 20 篇短文共享</div>
  <div id="chipBox"></div>
  <div class="panel-btns">
    <button id="btnReview">🃏 复习</button>
    <button id="btnCopy">复制全部</button>
    <button id="btnClear">清空</button>
  </div>
</div>
<div id="toast"></div>
<div id="reviewMask"><div class="rcard" style="position:relative"><button id="rClose">×</button><div id="rBox"></div>
  <div class="rbtns"><button id="rKeep">还不熟</button><button id="rKnown">已掌握</button></div>
</div></div>
<script>__JS__</script>
</body>
</html>
"""

meta = []
for n in range(1, 21):
    pj = json.load(open(os.path.join(PASS, 'List%02d.json' % n), encoding='utf-8'))
    skel = json.load(open(os.path.join(PASS, 'List%02d_skel.json' % n), encoding='utf-8'))
    zhf = json.load(open(os.path.join(PASS, 'List%02d_zh.json' % n), encoding='utf-8'))
    key = pj['list']
    assert zhf['list'] == key and skel['list'] == key
    words = words_data[key]
    list_lookup = {w['word'].strip().lower(): w for w in words.values()}
    extra_lookup = {k.strip().lower(): v for k, v in zhf['extra'].items()}
    zh_paras = zhf['zh']
    gram_by_sent = {(g['pid'], g['sid']): g for g in zhf['grammar']}

    day_m = re.search(r'Day\s*(\d+)', key)
    day = day_m.group(1) if day_m else '?'
    total_sents = sum(len(p) for p in skel['paragraphs'])
    nroot = sum(1 for w in words.values() if lookup_root(w['word'].strip().lower()))

    body_parts = []
    for pid, spara in enumerate(skel['paragraphs']):
        para_html = ['<div class="para">']
        for sid, sobj in enumerate(spara):
            en = sobj['en']
            zhtext = zh_paras[pid][sid]
            g = gram_by_sent.get((pid, sid))
            classes = 'sent' + (' has-gram' if g else '')
            data_en = html.escape(norm(en), quote=True)
            tools = ['<span class="st-tts" title="朗读整句">&#128264;</span>']
            if g:
                tools.append('<span class="st-gram" title="查看长难句语法拆解">🔷</span>')
            tools.append('<span class="st-zh" title="显示/隐藏本句译文">译</span>')
            en_html = render_en_text(en, list_lookup, extra_lookup, common_dict)
            sent_html = (f'<span class="{classes}" data-pid="{pid}" data-sid="{sid}" data-en="{data_en}">'
                         f'<span class="sent-tools">{"".join(tools)}</span>'
                         f'<span class="en-zone">{en_html}</span>'
                         f'<span class="zh">{html.escape(zhtext)}</span></span>')
            para_html.append(sent_html)
            if g:
                plain_en = norm(en)
                rows = []
                for ci, p in enumerate(g.get('parts', [])):
                    frag = ' '.join(norm(str(p.get('text', ''))).split())
                    rows.append('<tr><td class="role"><b>%d</b>%s</td><td class="frag">%s</td><td>%s</td></tr>' % (
                        ci + 1, html.escape(str(p.get('role', ''))),
                        html.escape(frag), html.escape(str(p.get('note', '')))))
                pts = ''.join('<li>%s</li>' % html.escape(str(x)) for x in g.get('points', []))
                gsent = highlight_grammar_sentence(plain_en, g.get('parts', []))
                card = (f'<div class="gram-card" id="card-{pid}-{sid}">'
                        f'<h4>🔷 长难句拆解｜{html.escape(g.get("title", ""))}</h4>'
                        f'<div class="skel">句子骨架：{html.escape(norm(g.get("skeleton", "")))}</div>'
                        f'<div class="gsent">{gsent}</div>'
                        f'<table>{"".join(rows)}</table>'
                        f'<ul class="pts">{pts}</ul>'
                        f'<div class="gzh">💬 {html.escape(zhtext)}</div>'
                        f'<div class="gacts"><span class="gtts" data-tts="{data_en}">&#128264; 朗读原句</span></div>'
                        f'</div>')
                para_html.append(card)
        para_html.append('</div>')
        body_parts.append(''.join(para_html))
    body = '\n'.join(body_parts)

    nav = []
    if n > 1: nav.append(f'<a href="List{n-1:02d}.html">← List {n-1}</a>')
    nav.append('<a href="index.html">返回目录</a>')
    if n < 20: nav.append(f'<a href="List{n+1:02d}.html">List {n+1} →</a>')

    page = (PAGE_TPL
            .replace('__TITLE__', f'十天搞定考研词汇 List{n} Day{day}｜埋词精读')
            .replace('__CSS__', CSS).replace('__JS__', JS + REVIEW_BELL_JS)
            .replace('__LISTKEY__', html.escape(key))
            .replace('__NAV__', ''.join(nav))
            .replace('__N__', str(n)).replace('__DAY__', day)
            .replace('__NWORDS__', str(len(words)))
            .replace('__NSENTS__', str(total_sents))
            .replace('__NEXTRA__', str(len(zhf['extra'])))
            .replace('__NGRAM__', str(len(zhf['grammar'])))
            .replace('__NROOT__', str(nroot))
            .replace('__BODY__', body))
    open(os.path.join(ROOT, 'List%02d.html' % n), 'w', encoding='utf-8').write(page)

    first_sent = norm(skel['paragraphs'][0][0]['en'])
    meta.append(dict(n=n, day=day, key=key, cat=key.split(' Day')[0],
                     nwords=len(words), nparas=len(skel['paragraphs']),
                     nsents=total_sents, nextra=len(zhf['extra']),
                     ngram=len(zhf['grammar']), desc=first_sent[:80]))
    print(f'List{n:02d}.html built: {len(words)} list-words, {total_sents} sents, '
          f'{len(zhf["extra"])} extra, {len(zhf["grammar"])} grammar cards')

# ---------------------------------------------------------------- roots center
roots60 = json.load(open(os.path.join(PASS, 'roots60.json'), encoding='utf-8'))
# word -> list locator
word_loc = {}
for li, lkey in enumerate(words_data.keys(), start=1):
    for info in words_data[lkey].values():
        word_loc.setdefault(info['word'].strip().lower(), li)

root_words = {rid: [] for rid in range(1, 61)}
nonroot_words = []
for lkey2, wmap in words_data.items():
    for info in wmap.values():
        w0 = info['word'].strip().lower()
        ln = word_loc[w0]
        item = {'w': info['word'].strip(), 'phon': info.get('phon', ''),
                'def': info.get('def', ''), 'ln': ln}
        rm = roots_map.get(w0)
        if rm:
            root_words[rm['rid']].append(dict(item, br=rm['br'], m=rm['m']))
        else:
            nonroot_words.append(item)

ROOTS_CSS = r"""
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif;background:#f4f6f8;color:#222;line-height:1.6;}
.wrap{max-width:1180px;margin:0 auto;padding:20px 20px 70px;}
.top{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:16px;}
.top h1{font-size:24px;color:#1f3a5f;}
.top a{padding:7px 16px;border-radius:18px;background:#fff;border:1px solid #d7dee8;color:#2b5797;text-decoration:none;font-size:13px;}
.top a:hover{background:#2b7cdd;color:#fff;border-color:#2b7cdd;}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;}
.stat{background:#fff;border-radius:14px;padding:16px 18px;box-shadow:0 3px 12px rgba(31,58,95,.07);border-top:4px solid #2b7cdd;}
.stat.g{border-top-color:#1c9e63;} .stat.gray{border-top-color:#9aa8b8;} .stat.gold{border-top-color:#e6a23c;}
.stat b{font-size:27px;color:#1f3a5f;display:block;}
.stat.g b{color:#138a55;} .stat.gray b{color:#6b7a8c;} .stat.gold b{color:#c87f10;}
.stat span{font-size:13px;color:#7a8799;}
.searchbar{background:#fff;border-radius:14px;padding:14px 18px;margin-bottom:16px;box-shadow:0 3px 12px rgba(31,58,95,.07);display:flex;gap:10px;flex-wrap:wrap;align-items:center;}
.searchbar input{flex:1;min-width:220px;padding:10px 15px;border:1px solid #d7dee8;border-radius:20px;font-size:14.5px;outline:none;}
.searchbar input:focus{border-color:#2b7cdd;}
.seg{display:inline-flex;border:1px solid #d7dee8;border-radius:20px;overflow:hidden;}
.seg button{border:none;background:#fff;padding:9px 18px;font-size:14px;color:#456;cursor:pointer;}
.seg button.on{background:#1c9e63;color:#fff;}
.hint{font-size:12.5px;color:#9aa8b8;width:100%;}
#searchRes{display:none;margin-bottom:16px;background:#fff;border-radius:14px;padding:8px 16px 14px;box-shadow:0 3px 12px rgba(31,58,95,.07);max-height:46vh;overflow:auto;}
#searchRes h3{font-size:14px;color:#1f3a5f;padding:10px 2px 6px;}
.rchip{display:inline-flex;flex-direction:column;vertical-align:top;width:300px;margin:6px 8px 0 0;padding:9px 12px;border-radius:10px;border:1px solid #e2e8f0;background:#fafcff;}
.rchip.yes{border-color:#bfe8d4;background:#f4fdf8;}
.rchip .l1{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
.rchip .rw{font-weight:bold;color:#2b5797;font-size:15px;}
.rchip .rp{color:#7a93ad;font-size:12.5px;}
.rchip .rtag{font-size:11px;border-radius:9px;padding:1px 8px;color:#fff;}
.rtag.g{background:#1c9e63;} .rtag.x{background:#9aa8b8;}
.rchip .rd{font-size:12.5px;color:#556;margin-top:3px;}
.rchip .br{font-size:12px;color:#138a55;margin-top:3px;}
.rchip a{font-size:12px;color:#2b7cdd;text-decoration:none;}
.grid60{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px;}
.rc{background:#fff;border-radius:14px;padding:15px 18px;box-shadow:0 3px 12px rgba(31,58,95,.07);border-left:5px solid #1c9e63;cursor:pointer;transition:transform .12s,box-shadow .12s;}
.rc:hover{transform:translateY(-2px);box-shadow:0 9px 22px rgba(28,158,99,.16);}
.rc h2{font-size:17px;color:#15613f;display:flex;align-items:center;gap:8px;}
.rc h2 .rid{background:#1c9e63;color:#fff;border-radius:8px;font-size:12px;padding:1px 8px;}
.rc .rcn{font-size:13.5px;color:#7a8799;margin:3px 0 6px;}
.rc .cnt{display:inline-block;font-size:12px;background:#eaf7f0;color:#138a55;border-radius:10px;padding:1px 10px;margin-right:6px;}
.rc .cnt2{display:inline-block;font-size:12px;background:#eef4fc;color:#2b5797;border-radius:10px;padding:1px 10px;}
.detail{display:none;border-top:1px dashed #d7e6dd;margin-top:11px;padding-top:10px;cursor:default;}
.rc.open .detail{display:block;}
.detail h4{font-size:12.5px;color:#8a96a5;margin:8px 0 5px;font-weight:normal;}
.ex{font-size:12.5px;color:#444;background:#f7faf8;border-radius:8px;padding:6px 10px;margin-bottom:4px;}
.ex b{color:#15613f;} .ex .exm{color:#7a8799;}
.wchip{display:inline-block;margin:3px 5px 3px 0;background:#eaf7f0;border:1px solid #cde9d9;border-radius:14px;padding:3px 10px;font-size:13px;}
.wchip a{color:#138a55;text-decoration:none;font-weight:bold;}
.wchip small{color:#8aa295;}
.wtip{display:none;position:absolute;max-width:300px;background:#2b2b2b;color:#eee;font-size:12px;padding:8px 11px;border-radius:8px;margin-top:4px;white-space:pre-wrap;z-index:90;box-shadow:0 6px 18px rgba(0,0,0,.25);line-height:1.55;text-align:left;}
.wchip{position:relative;}
.wchip:hover .wtip{display:block;}
.wtip .g{color:#8de0b4;}
.listh{font-size:16px;color:#1f3a5f;margin:20px 0 4px;border-left:4px solid #9aa8b8;padding-left:10px;}
.listh span{font-size:12.5px;color:#9aa8b8;font-weight:normal;margin-left:8px;}
.wrow{display:flex;gap:10px;align-items:baseline;padding:6px 4px;border-bottom:1px solid #edf1f5;font-size:13.5px;flex-wrap:wrap;}
.wrow .ww{font-weight:bold;color:#2b5797;min-width:150px;}
.wrow .wp{color:#8aa0b6;font-size:12.5px;min-width:120px;}
.wrow .wd{color:#556;flex:1;min-width:240px;}
@media (max-width:760px){.stats{grid-template-columns:repeat(2,1fr);}.rchip{width:100%;margin-right:0;}}
"""

client_data = {'roots': roots60, 'rootWords': {str(k): v for k, v in root_words.items()},
               'nonRoot': nonroot_words}
DATA_JSON = json.dumps(client_data, ensure_ascii=False)

roots_html_tpl = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>60 词根中心 · 十天搞定考研词汇</title>
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <h1>🌱 60 核心词根学习中心</h1>
    <div><a href="index.html">← 返回短文目录</a></div>
  </div>
  <div class="stats">
    <div class="stat"><b>3502</b><span>词表总词数</span></div>
    <div class="stat g"><b id="stYes">0</b><span>适用词根学习法（可拆解）</span></div>
    <div class="stat gray"><b id="stNo">0</b><span>不适用词根学习法（整体记忆）</span></div>
    <div class="stat gold"><b>60</b><span>核心词根（配 PDF 例词）</span></div>
  </div>
  <div class="searchbar">
    <input id="q" placeholder="🔍 输入任意单词查询分类，如 impose / attention / abandon（支持变形匹配）">
    <div class="seg" id="tabs">
      <button class="on" data-tab="roots">🌿 适用词根法 · 60 词根</button>
      <button data-tab="plain">📖 不适用词根法 · 按 List 查看</button>
    </div>
    <div class="hint">绿色＝该词可用这 60 个词根拆解记忆；灰色＝无对应核心词根（或属虚词/合成/词源不透明），建议整体记忆或结合短文语境记忆。点击词可跳转到对应埋词短文。</div>
  </div>
  <div id="searchRes"><h3 id="srHead"></h3><div id="srBox"></div></div>
  <div id="paneRoots"><div class="grid60" id="grid60"></div></div>
  <div id="panePlain" style="display:none"></div>
</div>
<script>
const DATA = __DATA__;
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
let nYes=0,nNo=DATA.nonRoot.length;
Object.values(DATA.rootWords).forEach(a=>nYes+=a.length);
document.getElementById('stYes').textContent=nYes;
document.getElementById('stNo').textContent=nNo;
function wchip(w){
  const tip='<span class="wtip">'+esc(w.phon)+'\\n'+esc(w.def)+'<span class="g">\\n🌱 '+esc(w.br)+'</span></span>';
  return '<span class="wchip"><a href="List'+String(w.ln).padStart(2,'0')+'.html">'+esc(w.w)+'</a>'+tip+'</span>';
}
function renderGrid(){
  const g=document.getElementById('grid60');
  g.innerHTML=DATA.roots.map(r=>{
    const ws=DATA.rootWords[String(r.id)]||[];
    const exs=r.examples.map(e=>'<div class="ex"><b>'+esc(e.w)+'</b>　'+esc(e.br)+' <span class="exm">'+esc(e.m)+'</span></div>').join('');
    const wc=ws.map(wchip).join('');
    return '<div class="rc" data-id="'+r.id+'"><h2><span class="rid">'+r.id+'</span>'+esc(r.roots.join(' / '))+' = '+esc(r.cn)+'</h2>'
      +'<div class="rcn">'+r.examples.length+' 个讲义例词</div>'
      +'<span class="cnt">词表 '+ws.length+' 词</span><span class="cnt2">点击展开/收起</span>'
      +'<div class="detail" onclick="event.stopPropagation()"><h4>📘 词根讲义例词</h4>'+exs
      +'<h4>📗 3502 词表中可拆的词（点击进入短文）</h4>'+(wc||'<span style="font-size:12px;color:#9aa8b8">本词表暂无</span>')+'</div></div>';
  }).join('');
  g.querySelectorAll('.rc').forEach(c=>c.addEventListener('click',()=>c.classList.toggle('open')));
}
function renderPlain(){
  const groups={};
  DATA.nonRoot.forEach(w=>{(groups[w.ln]=groups[w.ln]||[]).push(w);});
  const box=document.getElementById('panePlain');
  box.innerHTML=Object.keys(groups).sort((a,b)=>a-b).map(ln=>{
    const ws=groups[ln].sort((a,b)=>a.w.localeCompare(b.w));
    return '<div class="listh">List '+ln+' <span>'+ws.length+' 个词 · 建议结合埋词短文整体记忆</span></div>'
      +ws.map(w=>'<div class="wrow"><a class="ww" style="text-decoration:none" href="List'+String(ln).padStart(2,'0')+'.html">'+esc(w.w)+'</a><span class="wp">'+esc(w.phon)+'</span><span class="wd">'+esc(w.def)+'</span></div>').join('');
  }).join('');
}
renderGrid();renderPlain();
document.querySelectorAll('#tabs button').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('#tabs button').forEach(x=>x.classList.toggle('on',x===b));
  const t=b.dataset.tab;
  document.getElementById('paneRoots').style.display=t==='roots'?'':'none';
  document.getElementById('panePlain').style.display=t==='plain'?'':'none';
  document.getElementById('searchRes').style.display='none';
  document.getElementById('q').value='';
}));
/* search */
function lemmas(low){
  const c=new Set([low]);
  const add=x=>c.add(x);
  if(low.endsWith('ies')&&low.length>4)add(low.slice(0,-3)+'y');
  if(low.endsWith('es')&&low.length>3){add(low.slice(0,-2));add(low.slice(0,-1));}
  if(low.endsWith('s')&&!low.endsWith('ss')&&low.length>3)add(low.slice(0,-1));
  if(low.endsWith('ing')&&low.length>5){add(low.slice(0,-3));add(low.slice(0,-3)+'e');if(low.length>6&&low[-4]===low[-5])add(low.slice(0,-4));}
  if(low.endsWith('ed')&&low.length>4){add(low.slice(0,-2));add(low.slice(0,-1));}
  return c;
}
const allIdx=[];
Object.entries(DATA.rootWords).forEach(([rid,ws])=>ws.forEach(w=>allIdx.push({yes:true,w:String(w.w).toLowerCase(),rid:+rid,o:w})));
DATA.nonRoot.forEach(w=>allIdx.push({yes:false,w:String(w.w).toLowerCase(),o:w}));
document.getElementById('q').addEventListener('input',function(){
  const q=this.value.trim().toLowerCase();
  const box=document.getElementById('searchRes'),hb=document.getElementById('srHead'),sb=document.getElementById('srBox');
  if(!q){box.style.display='none';return;}
  const cands=lemmas(q);
  const hits=allIdx.filter(r=>r.w===q||cands.has(r.w)||r.w.startsWith(q)||q.length>=4&&r.w.includes(q)).slice(0,60);
  box.style.display='block';
  if(!hits.length){hb.textContent='未找到「'+this.value+'」（它可能不在 3502 词表中）';sb.innerHTML='';return;}
  const yes=hits.filter(h=>h.yes).length;
  hb.textContent='找到 '+hits.length+' 个结果 · '+yes+' 个适用词根法';
  sb.innerHTML=hits.map(h=>{
    const w=h.o;
    if(h.yes){const r=DATA.roots.find(x=>x.id===h.rid);
      return '<span class="rchip yes"><span class="l1"><a class="rw" style="text-decoration:none" href="List'+String(w.ln).padStart(2,'0')+'.html">'+esc(w.w)+'</a><span class="rp">'+esc(w.phon)+'</span><span class="rtag g">适用 · 词根'+h.rid+' '+esc(r.roots[0])+'＝'+esc(r.cn)+'</span></span><span class="rd">'+esc(w.def)+'</span><span class="br">🌱 '+esc(w.br)+'</span></span>';}
    return '<span class="rchip"><span class="l1"><a class="rw" style="text-decoration:none" href="List'+String(w.ln).padStart(2,'0')+'.html">'+esc(w.w)+'</a><span class="rp">'+esc(w.phon)+'</span><span class="rtag x">不适用 · List '+w.ln+'</span></span><span class="rd">'+esc(w.def)+'</span></span>';
  }).join('');
});
</script>
</body>
</html>
"""
open(os.path.join(ROOT, 'roots.html'), 'w', encoding='utf-8').write(
    roots_html_tpl.replace('__CSS__', ROOTS_CSS).replace('__DATA__', DATA_JSON)
    .replace('</script>\n</body>', REVIEW_BELL_JS + '\n</script>\n</body>'))
print('roots.html built: suitable=%d unsuitable=%d' % (sum(len(v) for v in root_words.values()), len(nonroot_words)))

# ---------------------------------------------------------------- review page (Ebbinghaus)
rv_lists = []
for n in range(1, 21):
    skel = json.load(open(os.path.join(PASS, 'List%02d_skel.json' % n), encoding='utf-8'))
    zhf = json.load(open(os.path.join(PASS, 'List%02d_zh.json' % n), encoding='utf-8'))
    key = skel['list']
    words = words_data[key]
    list_lookup = {w['word'].strip().lower(): w for w in words.values()}
    sents = []
    word_si = {}
    for pid, spara in enumerate(skel['paragraphs']):
        for sid, sobj in enumerate(spara):
            en = sobj['en']
            marks = MARK.findall(en)
            if not marks:
                continue
            si_store = len(sents)
            sents.append({'en': en, 'zh': zhf['zh'][pid][sid]})
            for f in marks:
                low = f.strip().lower()
                for cand in lemma_candidates(low):
                    if cand in list_lookup:
                        word_si.setdefault(cand, []).append((low == cand, si_store))
    rwords = []
    for info in words.values():
        w0 = info['word'].strip()
        low = w0.lower()
        pairs = sorted(set(word_si.get(low, [])), key=lambda t: (not t[0], t[1]))[:2]
        item = {'w': w0, 'phon': info.get('phon', ''), 'def': info.get('def', ''),
                'si': [t[1] for t in pairs]}
        rm = roots_map.get(low)
        if rm:
            item['r'] = rm['br']
        rwords.append(item)
    rv_lists.append({'key': key, 'words': rwords, 'sents': sents})
    n_noex = sum(1 for x in rwords if not x['si'])
    print('review data List%02d: %d words, %d sents, no-example=%d' % (n, len(rwords), len(sents), n_noex))

# --- build global pool + compute similar-word distractors for 4-choice quiz ---
import difflib, random
pool = []  # flat list of all {n, w, def}
for li, l in enumerate(rv_lists):
    for wi, w in enumerate(l['words']):
        pool.append({'n': li + 1, 'wi': wi, 'w': w['w'], 'def': w.get('def', '')})

def similar_distractors(target_w, target_def, k=3):
    """Return k pool indices of words similar in spelling but with distinct meaning."""
    tw = target_w.lower()
    tl = len(tw)
    seen_defs = {target_def}
    scored = []
    for idx, p in enumerate(pool):
        pw = p['w'].lower()
        if pw == tw:
            continue
        if abs(len(pw) - tl) > 3:
            continue
        ratio = difflib.SequenceMatcher(None, tw, pw).ratio()
        # prefer same prefix letter + similar length
        if pw[0] == tw[0]:
            ratio += 0.12
        if abs(len(pw) - tl) <= 1:
            ratio += 0.08
        scored.append((ratio, idx))
    scored.sort(reverse=True)
    picks = []
    for _, idx in scored:
        d = pool[idx]['def']
        if d in seen_defs:
            continue
        seen_defs.add(d)
        picks.append(idx)
        if len(picks) >= k:
            break
    # fallback: random distinct-meaning words if not enough similar
    if len(picks) < k:
        fallback = list(range(len(pool)))
        random.shuffle(fallback)
        for idx in fallback:
            if idx in picks or pool[idx]['w'].lower() == tw:
                continue
            d = pool[idx]['def']
            if d in seen_defs:
                continue
            seen_defs.add(d)
            picks.append(idx)
            if len(picks) >= k:
                break
    return picks

for p in pool:
    li, wi = p['n'] - 1, p['wi']
    rv_lists[li]['words'][wi]['dists'] = similar_distractors(p['w'], p['def'], 3)

n_no_dist = sum(1 for l in rv_lists for w in l['words'] if len(w.get('dists', [])) < 3)
print('distractors computed; words with <3 distractors: %d' % n_no_dist)

RV_DATA_JSON = json.dumps({'lists': rv_lists}, ensure_ascii=False)

REVIEW_CSS = r"""
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:"Microsoft YaHei","PingFang SC",Arial,sans-serif;background:#f4f6f8;color:#222;line-height:1.6;}
.wrap{max-width:1000px;margin:0 auto;padding:20px 20px 70px;}
.top{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:16px;}
.top h1{font-size:23px;color:#1f3a5f;}
.top a{padding:7px 14px;border-radius:18px;background:#fff;border:1px solid #d7dee8;color:#2b5797;text-decoration:none;font-size:13px;margin-left:6px;display:inline-block;}
.top a:hover{background:#2b7cdd;color:#fff;border-color:#2b7cdd;}
.statrow{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;}
.stat{background:#fff;border-radius:14px;padding:14px 16px;box-shadow:0 3px 12px rgba(31,58,95,.07);border-top:4px solid #2b7cdd;text-align:center;}
.stat b{font-size:24px;color:#1f3a5f;display:block;}
.stat span{font-size:12.5px;color:#7a8799;}
.stat.o{border-top-color:#e6a23c;}.stat.o b{color:#c87f10;}
.stat.g{border-top-color:#1c9e63;}.stat.g b{color:#138a55;}
.stat.p{border-top-color:#7a67d8;}.stat.p b{color:#5b48c0;}
.box{background:#fff;border-radius:14px;padding:16px 20px;margin-bottom:16px;box-shadow:0 3px 12px rgba(31,58,95,.07);}
.box h2{font-size:16px;color:#1f3a5f;margin-bottom:10px;}
.box h2 small{font-weight:normal;color:#8a96a5;font-size:12.5px;margin-left:8px;}
.row{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:10px 4px;border-bottom:1px solid #f0f3f7;}
.row:last-child{border-bottom:none;}
.tag{font-size:12px;background:#eef4fc;color:#2b5797;border-radius:10px;padding:2px 10px;}
.tag.o{background:#fdf3e0;color:#c87f10;}
.tag.g{background:#eaf7f0;color:#138a55;}
.btn{border:none;border-radius:18px;padding:8px 20px;font-size:13.5px;cursor:pointer;color:#fff;background:#2b7cdd;}
.btn:hover{background:#1f66c2;}
.btn.g{background:#1c9e63;}.btn.g:hover{background:#138a55;}
.btn.p{background:#7a67d8;}.btn.p:hover{background:#6552c4;}
.mini{border:1px solid #d7dee8;background:#fff;border-radius:14px;padding:4px 12px;font-size:12px;color:#2b5797;cursor:pointer;}
.mini:hover{border-color:#2b7cdd;}
.muted{color:#9aa8b8;font-size:12.5px;}
.uprow{padding:7px 4px;border-bottom:1px dashed #eef1f5;font-size:13px;color:#7a8799;display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
table.plan{width:100%;border-collapse:collapse;font-size:13px;}
table.plan td{border-top:1px solid #f0f3f7;padding:7px 6px;vertical-align:middle;}
table.plan td:first-child{color:#c87f10;font-weight:bold;white-space:nowrap;width:110px;}
/* session */
#sess{position:fixed;inset:0;background:linear-gradient(160deg,#eef4fc,#f8fbff);z-index:900;overflow:auto;padding:16px 14px 46px;}
.sess-top{max-width:640px;margin:0 auto 8px;display:flex;align-items:center;gap:10px;}
#sExit{border:1px solid #d7dee8;background:#fff;border-radius:16px;padding:6px 14px;font-size:13px;color:#5a6a7d;cursor:pointer;}
#sExit:hover{border-color:#2b7cdd;color:#2b7cdd;}
.sprog{flex:1;font-size:13px;color:#5a6f88;}
.smode{font-size:12px;color:#fff;background:#2b7cdd;border-radius:10px;padding:2px 10px;white-space:nowrap;}
.sbar{max-width:640px;margin:0 auto 18px;height:5px;background:#dbe6f2;border-radius:4px;overflow:hidden;}
#sBarFill{height:100%;width:0;background:linear-gradient(90deg,#2b7cdd,#56a3f0);transition:width .2s;}
.shead{max-width:640px;margin:0 auto 10px;display:flex;justify-content:center;gap:16px;flex-wrap:wrap;font-size:13px;color:#5a6f82;background:rgba(255,255,255,.78);border:1px solid #e2e8f0;border-radius:12px;padding:7px 12px;}
.shead b{color:#1f66c2;font-variant-numeric:tabular-nums;}
/* 5分钟/30分钟复习阶段：背景与学习界面区分开 */
#sess.ph-r5{background:linear-gradient(160deg,#fdf3dc,#fef9ec);}
#sess.ph-r5 .card{background:#fffdf3;border:1px solid #eed9a4;}
#sess.ph-r5 .smode{background:#e6a23c;}
#sess.ph-r5 #sBarFill{background:linear-gradient(90deg,#e6a23c,#f0c060);}
#sess.ph-r5 .shead{background:rgba(255,255,255,.88);border-color:#ecd9a3;color:#8a6d2b;}
#sess.ph-r30{background:linear-gradient(160deg,#fdeadd,#fef4ea);}
#sess.ph-r30 .card{background:#fffaf2;border:1px solid #f0c9a0;}
#sess.ph-r30 .smode{background:#e0803c;}
#sess.ph-r30 #sBarFill{background:linear-gradient(90deg,#e0803c,#e6a23c);}
#sess.ph-r30 .shead{background:rgba(255,255,255,.88);border-color:#ecc9a3;color:#9c5e1e;}
.card{max-width:640px;margin:0 auto;background:#fff;border-radius:18px;box-shadow:0 10px 34px rgba(31,58,95,.14);padding:30px 32px 22px;min-height:400px;display:flex;flex-direction:column;}
.cfront{display:flex;flex-direction:column;gap:10px;}
.ctimer{text-align:center;font-size:14px;color:#7a93ad;font-variant-numeric:tabular-nums;letter-spacing:.5px;}
.ctimer b{color:#1f66c2;font-weight:bold;}
.cw{font-size:40px;font-weight:bold;color:#1f3a5f;text-align:center;line-height:1.25;}
.cph{text-align:center;color:#5a83b8;font-size:16px;margin-top:2px;}
.csp{display:block;margin:6px auto 0;background:#eef4fc;border:none;border-radius:16px;padding:6px 18px;font-size:14px;color:#2b5797;cursor:pointer;}
.flipHint{text-align:center;color:#b3c2d4;font-size:12.5px;margin-top:4px;}
.cfront .cbtns{margin:14px 0 0;}
.cback{display:none;flex-direction:column;gap:9px;}
.card.flip .cfront{display:none;}
.card.flip .cback{display:flex;}
.cdef{font-size:17px;color:#333;text-align:center;line-height:1.7;}
.croot{font-size:13px;color:#138a55;background:#f2fbf6;border:1px dashed #bfe8d4;border-radius:8px;padding:6px 12px;text-align:center;}
.cex{background:#f8fafd;border-left:3px solid #b9d4f5;border-radius:0 8px 8px 0;padding:8px 12px;}
.cex .en{font-size:14.5px;color:#2b2b2b;line-height:1.75;}
.cex .zh{font-size:12.5px;color:#7a8799;margin-top:3px;line-height:1.6;}
mark.thl{background:#dff0ff;color:#1f66c2;font-weight:bold;padding:0 2px;border-radius:3px;}
.kbd{text-align:center;font-size:11.5px;color:#a9b8c9;margin-top:4px;}
.cused{text-align:center;font-size:12.5px;color:#8a96a5;margin-top:6px;}
.cnext{display:block;margin:10px auto 0;border:none;border-radius:18px;padding:9px 34px;font-size:14.5px;cursor:pointer;color:#fff;background:#2b7cdd;}
.cnext:hover{background:#1f66c2;}
.cbtns{display:flex;gap:10px;width:100%;}
.cbtns button{border:none;border-radius:18px;padding:10px 0;flex:1;font-size:13.5px;cursor:pointer;color:#fff;}
#bNo{background:#e08b6f;}#bNo:hover{background:#cf6f4f;}
#bMid{background:#e6a23c;}#bMid:hover{background:#cf8a1c;}
#bQuiz{background:#2b7cdd;}#bQuiz:hover{background:#1f66c2;}
#bYes{background:#37b37c;}#bYes:hover{background:#2c9866;}
.cbtns button:disabled{opacity:.35;cursor:not-allowed;}
/* 4-choice quiz overlay */
#quizMask{display:none;position:fixed;inset:0;background:rgba(20,30,45,.7);z-index:3100;align-items:center;justify-content:center;padding:18px;}
#quizMask.show{display:flex;}
.qbox{background:#fff;border-radius:18px;width:min(560px,94vw);padding:22px 24px;box-shadow:0 20px 60px rgba(0,0,0,.4);}
.qbox .qh{font-size:15px;color:#5a6f82;margin-bottom:6px;}
.qbox .qw{font-size:30px;font-weight:bold;color:#1f3a5f;text-align:center;margin-bottom:4px;}
.qbox .qph{text-align:center;color:#7a93ad;font-size:14px;margin-bottom:14px;}
.qbox .qask{text-align:center;font-size:13.5px;color:#8a96a5;margin-bottom:14px;}
.qopts{display:flex;flex-direction:column;gap:9px;}
.qopt{border:1.5px solid #e2e8f0;border-radius:12px;padding:12px 16px;font-size:14.5px;color:#333;background:#fafcff;cursor:pointer;text-align:left;line-height:1.5;transition:border-color .12s,background .12s;}
.qopt:hover{border-color:#2b7cdd;background:#eef4fc;}
.qopt.correct{border-color:#37b37c;background:#eafaf1;color:#138a55;font-weight:bold;}
.qopt.wrong{border-color:#e08b6f;background:#fdeeec;color:#c0392b;}
.qopt.disabled{cursor:default;opacity:.6;}
.qfb{text-align:center;margin-top:12px;font-size:13.5px;min-height:20px;}
.qfb.ok{color:#138a55;}.qfb.no{color:#c0392b;}
.qnext{display:block;margin:14px auto 0;border:none;border-radius:18px;padding:8px 26px;font-size:14px;cursor:pointer;color:#fff;background:#2b7cdd;}
.qnext:hover{background:#1f66c2;}
.qnext:disabled{opacity:.35;cursor:not-allowed;}
.done{max-width:640px;margin:40px auto;text-align:center;background:#fff;border-radius:18px;padding:40px 30px;box-shadow:0 10px 34px rgba(31,58,95,.14);}
.done h2{color:#138a55;font-size:22px;margin-bottom:12px;}
.done p{color:#5a6f82;font-size:14.5px;line-height:2;}
#toast{position:fixed;left:50%;bottom:34px;transform:translateX(-50%);background:#333;color:#fff;padding:10px 22px;border-radius:22px;font-size:13.5px;opacity:0;transition:opacity .25s;z-index:2000;pointer-events:none;}
#toast.show{opacity:.94;}
/* countdown card */
#cdBox .cdtime{font-size:32px;font-weight:bold;color:#1f66c2;font-variant-numeric:tabular-nums;letter-spacing:1px;line-height:1.2;}
#cdBox .cdlab{font-size:13px;color:#8a96a5;margin-top:3px;}
#cdBox .cdnext{font-size:14.5px;color:#456;margin-bottom:4px;}
.cdurgent{display:flex;align-items:center;gap:14px;flex-wrap:wrap;background:linear-gradient(90deg,#fff3e0,#ffe9d2);border:1px solid #f0c48a;border-radius:12px;padding:13px 18px;animation:cdpulse 1.3s infinite;}
.cdurgent .cdn{font-size:20px;font-weight:bold;color:#c87f10;}
@keyframes cdpulse{0%,100%{box-shadow:0 0 0 0 rgba(230,162,60,.45);}50%{box-shadow:0 0 0 10px rgba(230,162,60,0);}}
/* 40天经典计划表 */
.ptbl{width:100%;border-collapse:collapse;font-size:13px;}
.ptbl th,.ptbl td{border:1px solid #e2e8f0;padding:4px 3px;text-align:center;min-width:50px;}
.ptbl th{background:#f4f8ff;color:#5a6f82;font-weight:normal;font-size:12px;}
.ptbl td.rowlab{background:#fafbfd;color:#8a96a5;font-size:12px;white-space:nowrap;min-width:40px;}
.ptbl td.today,.ptbl th.today{background:#fff3da;box-shadow:inset 0 0 0 2px #e6a23c;}
.pchip{display:inline-block;margin:1px 2px;padding:2px 8px;border-radius:10px;font-weight:bold;cursor:pointer;font-size:13px;border:1px solid transparent;}
.pchip.new{background:#eaf3ff;color:#2b7cdd;border-color:#c3d9f5;}
.pchip.new:hover{background:#2b7cdd;color:#fff;}
.pchip.chk{background:#eafaf1;color:#1c9e63;border-color:#bfe8d2;}
.pchip.chk:hover{background:#1c9e63;color:#fff;}
.pchip.done{background:#f0f1f3;color:#a9b3bd;text-decoration:line-through;border-color:#e2e8f0;}
@media (max-width:640px){.statrow{grid-template-columns:repeat(2,1fr);}.card{padding:22px 18px;min-height:340px;}.cw{font-size:32px;}.cbtns button{font-size:13px;}}
"""

REVIEW_JS = r"""
const DATA=__RVDATA__;
const IVL=[5*6e4,30*6e4,12*36e5,864e5,2*864e5,4*864e5,7*864e5,15*864e5];
const LAB=['5分钟','30分钟','12小时','1天','2天','4天','7天','15天'];
const SKEY='ky_review_v1';
let RV={start:null,words:{}};
try{const raw=JSON.parse(localStorage.getItem(SKEY)||'null');if(raw&&raw.words)RV=raw;}catch(e){}
Object.keys(RV.words).forEach(k=>{const st=RV.words[k];if(st&&st.t0===undefined)st.t0=st.t;});
if(!RV.checks)RV.checks={};
let prefs={};try{Object.assign(prefs,JSON.parse(localStorage.getItem('ky_prefs_v2')||'{}'));}catch(e){}
function save(){localStorage.setItem(SKEY,JSON.stringify(RV));}
/* 到期时刻：第1轮(5分钟)/第2轮(30分钟) 按「上一轮完成时刻」重新计时；
   第3轮起(12小时/1天/2天/4天/7天/15天) 按首次学习的总时间计算 */
function nextDue(st){if(!st||st.s>=8)return null;return (st.s<=1?st.t:st.t0)+IVL[st.s];}
const BACK=(()=>{try{const b=new URLSearchParams(location.search).get('back')||'';return /^[\w-]+\.html$/.test(b)?b:'';}catch(e){return '';}})();
const origTitle=document.title;
let cdInt=null,titleInt=null,cdKey='',lastDueSeen=0;
function beep(){try{const C=window.AudioContext||window.webkitAudioContext;const ctx=beep.ctx||(beep.ctx=new C());
  const o=ctx.createOscillator(),g=ctx.createGain();o.connect(g);g.connect(ctx.destination);
  o.frequency.value=880;g.gain.setValueAtTime(0.12,ctx.currentTime);g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+0.6);
  o.start();o.stop(ctx.currentTime+0.6);}catch(e){}}
function fmtCD(ms){const s=Math.max(0,Math.ceil(ms/1000));
  if(s<3600)return Math.floor(s/60)+'分'+String(s%60).padStart(2,'0')+'秒';
  const h=Math.floor(s/3600);if(h<48)return h+'小时'+Math.floor(s%3600/60)+'分';
  return Math.floor(h/24)+'天'+(h%24)+'小时';}
let toastTm;
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');clearTimeout(toastTm);toastTm=setTimeout(()=>t.classList.remove('show'),1600);}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function lemmas(low){
  const c=new Set([low]);const add=x=>c.add(x);
  if(low.endsWith('ies')&&low.length>4)add(low.slice(0,-3)+'y');
  if(low.endsWith('ied')&&low.length>4)add(low.slice(0,-3)+'y');
  if(low.endsWith('es')&&low.length>3){add(low.slice(0,-2));add(low.slice(0,-1));}
  if(low.endsWith('s')&&!low.endsWith('ss')&&low.length>3)add(low.slice(0,-1));
  if(low.endsWith('ing')&&low.length>5){add(low.slice(0,-3));add(low.slice(0,-3)+'e');if(low.length>6&&low[low.length-4]===low[low.length-5])add(low.slice(0,-4));}
  if(low.endsWith('ed')&&low.length>4){add(low.slice(0,-2));add(low.slice(0,-1));if(low.length>5&&low[low.length-3]===low[low.length-4])add(low.slice(0,-3));}
  if(low.endsWith('er')&&low.length>4)add(low.slice(0,-2));
  if(low.endsWith('est')&&low.length>5)add(low.slice(0,-3));
  if(low.endsWith('ly')&&low.length>3)add(low.slice(0,-2));
  return c;
}
function fmtLeft(ms){if(ms<=0)return '现在';const m=Math.ceil(ms/6e4);if(m<60)return m+'分钟后';const h=Math.ceil(m/60);if(h<=36)return h+'小时后';return Math.ceil(h/24)+'天后';}
function todayStr(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
function midOf(s){const p=s.split('-');return new Date(+p[0],+p[1]-1,+p[2]).getTime();}
let voices=[];function loadVoices(){voices=speechSynthesis.getVoices()||[];}
if('speechSynthesis' in window){loadVoices();speechSynthesis.onvoiceschanged=loadVoices;}
let _utter=null,_spkTm=null;
function speak(t){if(!('speechSynthesis' in window))return;speechSynthesis.cancel();if(_spkTm)clearTimeout(_spkTm);_spkTm=setTimeout(function(){const u=new SpeechSynthesisUtterance(t);_utter=u;u.lang=prefs.accent||'en-US';u.rate=0.88;const v=voices.find(v=>v.lang===u.lang)||voices.find(v=>v.lang&&v.lang.startsWith(u.lang.slice(0,2)));if(v){u.voice=v;u.lang=v.lang;}u.onend=u.onerror=function(){if(_utter===u)_utter=null;};speechSynthesis.speak(u);},80);}
const TOTAL=DATA.lists.reduce((a,l)=>a+l.words.length,0);
const POOL=[];DATA.lists.forEach(l=>l.words.forEach(w=>POOL.push(w)));
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function learnedOf(n){let c=0;DATA.lists[n-1].words.forEach(w=>{if(RV.words[n+'/'+w.w])c++;});return c;}
function dayNow(){if(!RV.start)return null;return Math.floor((midOf(todayStr())-midOf(RV.start))/864e5)+1;}
function dueData(){
  const due=[],up=[];const now=Date.now();
  Object.keys(RV.words).forEach(k=>{const st=RV.words[k];const d0=nextDue(st);if(d0===null)return;const left=d0-now;
    (left<=0?due:up).push({k,n:+k.split('/')[0],s:st.s,left:Math.max(0,left)});});
  const g={};due.forEach(d=>{const key=d.n+'|'+d.s;(g[key]=g[key]||{n:d.n,s:d.s,keys:[]}).keys.push(d.k);});
  return {groups:Object.values(g).sort((a,b)=>a.n-b.n||a.s-b.s),up:up.sort((a,b)=>a.left-b.left),total:due.length};
}
/* ---- 经典40天艾宾浩斯表（十天搞定考研词汇原版安排） ---- */
const PNAMES=['A','B','C','D','E','F','G','H','I','J'];
const PLISTS=[[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13,14],[15,16],[17,18],[19,20]];
const TBL_AM={1:[0],2:[1],3:[2],4:[3],5:[4],6:[5],7:[6],8:[0,7],9:[1,8],10:[2,9],11:[3],12:[4],13:[5],14:[6],15:[0,7],16:[1,8],17:[2,9],18:[3],19:[4],20:[5],21:[6],22:[7],23:[8],24:[9],30:[0],31:[1],32:[2],33:[3],34:[4],35:[5],36:[6],37:[7],38:[8],39:[9]};
const TBL_PM={1:[0],2:[0,1],3:[1,2],4:[0,2,3],5:[1,3,4],6:[2,4,5],7:[3,5,6],8:[4,6,7],9:[5,7,8],10:[6,8,9],11:[7,9],12:[8],13:[9]};
function partChip(d,pi,when){
  const isNew=(when==='am'&&pi===d-1&&d<=10);
  const lists=PLISTS[pi];
  const tip=PNAMES[pi]+' = List '+String(lists[0]).padStart(2,'0')+'-'+String(lists[1]).padStart(2,'0')+(isNew?' · 上午新学':' · 检查');
  let done;
  if(isNew)done=lists.every(n=>learnedOf(n)>=DATA.lists[n-1].words.length);
  else done=!!(RV.checks&&RV.checks[d+':'+pi]);
  return '<span class="pchip '+(done?'done':(isNew?'new':'chk'))+'" data-pt="'+d+'|'+pi+'|'+(isNew?'n':'c')+'" title="'+tip+'">'+PNAMES[pi]+'</span>';
}
function buildTbl(dn){
  let h='<table class="ptbl">';
  [[1,10],[11,20],[21,30],[31,40]].forEach(bd=>{
    h+='<tr><td class="rowlab">天数</td>';
    for(let d=bd[0];d<=bd[1];d++)h+='<th'+(d===dn?' class="today"':'')+'>'+d+'</th>';
    h+='</tr>';
    [['am','上午'],['pm','晚上']].forEach(rw=>{
      h+='<tr><td class="rowlab">'+rw[1]+'</td>';
      for(let d=bd[0];d<=bd[1];d++){
        const arr=(rw[0]==='am'?TBL_AM:TBL_PM)[d]||[];
        h+='<td'+(d===dn?' class="today"':'')+'>'+arr.map(pi=>partChip(d,pi,rw[0])).join('')+'</td>';
      }
      h+='</tr>';
    });
  });
  return h+'</table>';
}
function openPartCheck(d,pi){
  const items=[];
  PLISTS[pi].forEach(n=>DATA.lists[n-1].words.forEach(w=>{const k=n+'/'+w.w;if(RV.words[k])items.push({k,n,wd:w});}));
  if(!items.length){toast(PNAMES[pi]+' 部分（List '+PLISTS[pi].map(x=>String(x).padStart(2,'0')).join('-')+'）还没有已学单词，先完成新学');return;}
  S={mode:'rev',n:0,queue:shuffle(items),again:[],idx:0,total:items.length,touched:[],checkKey:d+':'+pi};
  startSess('🔄 第'+d+'天检查 · '+PNAMES[pi]+'（List '+PLISTS[pi].map(x=>String(x).padStart(2,'0')).join('-')+'）');
}
function renderDash(){
  const box=document.getElementById('dash');
  if(!RV.start){
    box.innerHTML='<div class="box"><h2>设置开始日期</h2><p class="muted">十天背完 3502 词：每天新学 2 个 List，新词在 <b>5分钟 / 30分钟 / 12小时 / 1天 / 2天 / 4天 / 7天 / 15天</b> 共 8 个遗忘临界点自动安排复习。例句自动摘自 20 篇埋词短文。选好开始日期即可。</p>'
      +'<div class="row" style="border:none;margin-top:10px"><input type="date" id="startDate" value="'+todayStr()+'" style="padding:8px 12px;border:1px solid #d7dee8;border-radius:10px;font-size:14px">'
      +'<button class="btn" id="startBtn">📅 开始 10 天计划</button></div></div>';
    document.getElementById('startBtn').addEventListener('click',()=>{RV.start=document.getElementById('startDate').value||todayStr();save();renderDash();toast('计划已开始：'+RV.start);});
    return;
  }
  const dn=dayNow();const dd=dueData();
  let learned=0,grad=0;Object.keys(RV.words).forEach(k=>{learned++;if(RV.words[k].s>=8)grad++;});
  let h='<div class="statrow">'
    +'<div class="stat o"><b>'+(dn<1?'—':(dn>10?'10+':dn))+'</b><span>计划第几天 / 共10天</span></div>'
    +'<div class="stat"><b>'+learned+'</b><span>已新学 / 共 '+TOTAL+' 词</span></div>'
    +'<div class="stat g"><b>'+grad+'</b><span>完成全部8轮复习</span></div>'
    +'<div class="stat p"><b>'+dd.total+'</b><span>当前到期待复习</span></div></div>';
  h+='<div class="box" id="cdBox"><h2>⏰ 复习倒计时 <small>每轮完成后重新计时 · 5分钟/30分钟按上轮完成时刻算 · 12小时起按首次学习总时间算</small></h2><div id="cdBody"></div></div>';
  h+='<div class="box"><h2>📥 今日新学 <small>'+esc(RV.start)+' 开始 · 每日 2 个 List</small></h2>';
  if(dn>=1&&dn<=40){
    const fmtT=(arr,when)=>arr.length?arr.map(pi=>{const isNew=(when==='am'&&pi===dn-1&&dn<=10);return (isNew?'新学':'检查')+PNAMES[pi];}).join('、'):'—';
    h+='<p style="margin-bottom:8px;font-size:13.5px;color:#5a6f82">📅 按经典表，今天（第 '+dn+' 天）：<b>上午</b> '+fmtT(TBL_AM[dn]||[],'am')+' ・ <b>晚上</b> '+fmtT(TBL_PM[dn]||[],'pm')+'（点击下表字母可直接开始）</p>';
  }
  if(dn<1)h+='<p class="muted">计划开始日期在将来，尚未开始。可在下方总计划表提前学习。</p>';
  else if(dn>10)h+='<p class="muted">🎉 10 天新学任务已全部完成！到期的复习会继续按遗忘曲线出现在下面。</p>';
  else [2*dn-1,2*dn].forEach(n=>{const c=learnedOf(n),t=DATA.lists[n-1].words.length;
    h+='<div class="row"><span class="tag">Day '+dn+'</span><b>List '+String(n).padStart(2,'0')+'</b><span class="muted">'+esc(DATA.lists[n-1].key)+'</span><span class="muted">'+c+'/'+t+'</span>'
      +(c>=t?'<span class="tag g">✓ 已学完</span>':'<button class="btn g" data-new="'+n+'">开始新学 · '+t+' 词</button>')+'</div>';});
  if(dn>=1&&dn<=10){
    const remA=DATA.lists[2*dn-2].words.length-learnedOf(2*dn-1),remB=DATA.lists[2*dn-1].words.length-learnedOf(2*dn);
    if(remA+remB>0)h+='<div class="row" style="border:none;background:#f4f8ff;border-radius:10px"><span class="muted">推荐：</span><button class="btn p" id="day2Btn">▶ 连续学完今天两个 List（还剩 '+(remA+remB)+' 新词）</button><span class="muted">学习中每 5 分钟原地复习本周期词、每 30 分钟复习周期池，不跳转页面</span></div>';
  }
  h+='</div>';
  h+='<div class="box"><h2>📅 40 天总计划表 <small>经典艾宾浩斯表 · 蓝=上午新学 · 绿=检查 · 点击字母直接开始 · 金框=今天</small></h2>';
  h+='<p class="muted" style="margin-bottom:8px;font-size:12.5px">A=List01-02 · B=List03-04 · C=List05-06 · D=List07-08 · E=List09-10 · F=List11-12 · G=List13-14 · H=List15-16 · I=List17-18 · J=List19-20　|　每部分贯彻 5分钟→30分钟→12小时→1天→2天→4天→7天→15天 八临界点后，还需每隔15天检查直至考前</p>';
  h+=buildTbl(dn);
  h+='</div>';
  h+='<div class="box"><h2>🔔 到期复习 <small>遗忘曲线 8 临界点：'+LAB.join(' → ')+'</small></h2>';
  if(!dd.groups.length){
    h+='<p class="muted">当前没有到期的复习。'+(dd.up.length?'最近一轮：<b>List '+String(dd.up[0].n).padStart(2,'0')+'</b> 第'+(dd.up[0].s+1)+'轮（'+LAB[dd.up[0].s]+'）· <b>'+fmtLeft(dd.up[0].left)+'</b>到期':'先在上方或总计划表中完成新学。')+'</p>';
  }else{
    dd.groups.forEach(gd=>{h+='<div class="row"><span class="tag">List '+String(gd.n).padStart(2,'0')+'</span><b>第'+(gd.s+1)+'轮 · '+LAB[gd.s]+'</b><span class="muted">'+gd.keys.length+' 词到期</span><button class="btn p" data-rev="'+gd.n+'|'+gd.s+'">开始复习</button></div>';});
    if(dd.groups.length>1)h+='<div class="row"><span class="muted">时间充裕？把今天到期的合并过一遍：</span><button class="btn" data-revall="1">🔄 复习全部到期（'+dd.total+' 词）</button></div>';
  }
  if(dd.up.length)h+='<div style="margin-top:8px">'+dd.up.slice(0,4).map(u=>'<div class="uprow">⏳ List '+String(u.n).padStart(2,'0')+' · 第'+(u.s+1)+'轮（'+LAB[u.s]+'）· <b>'+fmtLeft(u.left)+'</b>到期</div>').join('')+(dd.up.length>4?'<div class="uprow" style="border:none">…另有 '+(dd.up.length-4)+' 轮未到期</div>':'')+'</div>';
  h+='</div>';
  h+='<div class="box"><h2>🗓 10 天总计划 <small>新词学完后按 8 个临界点自动排复习</small></h2><table class="plan">';
  for(let d=1;d<=10;d++){
    const cells=[2*d-1,2*d].map(n=>{const c=learnedOf(n),t=DATA.lists[n-1].words.length;
      return '<td>List '+String(n).padStart(2,'0')+' <span class="muted">'+c+'/'+t+'</span> '+(c<t?'<button class="mini" data-new="'+n+'">学</button>':'<span class="tag g" style="font-size:11px">✓</span>')+'</td>';}).join('');
    h+='<tr'+(dn===d?' style="background:#fff8ec"':'')+'><td>Day '+d+(dn===d?' <span class="tag o" style="font-size:11px">今天</span>':'')+'</td>'+cells+'</tr>';
  }
  h+='</table></div>';
  h+='<div class="box"><h2>⚙️ 设置</h2><div class="row" style="border:none"><span class="muted">开始日期</span><input type="date" id="startDate2" value="'+RV.start+'" style="padding:6px 10px;border:1px solid #d7dee8;border-radius:10px;font-size:13px"><button class="mini" id="chStart">保存</button><button class="mini" id="resetBtn" style="color:#c0392b">重置全部进度</button></div><p class="muted" style="margin-top:8px">判定规则：<b>认识</b>＝弹出 4 选 1（3 个干扰项来自拼写相似词的释义），答对进入下一轮、答错本轮再过一次；<b>完全认识</b>＝直接进入下一轮；<b>模糊</b>＝本轮再过一次并进入下一轮；<b>不认识</b>＝重置回第1轮（5分钟）。</p><p class="muted">计时规则：学习界面顶部同时显示<b>总计时</b>和<b>5分钟周期倒计时</b>，互不冲突——每满 5 分钟<b>在当前页面原地</b>复习本周期所学（背景变为米色，不跳转），复习完开启新的 5 分钟周期、单词进入 30 分钟池；按总计时每满 30 分钟原地复习一次 30 分钟池（背景变为橙色）；当天两个 List 学完后全部单词进入「12小时后」队列，之后按首次学习总时间推进 1天 → 2天 → 4天 → 7天 → 15天，到点响铃+跨页右下角提醒。进度保存在本机浏览器，与生词本互相独立。</p></div>';
  box.innerHTML=h;
  box.querySelectorAll('[data-new]').forEach(b=>b.addEventListener('click',()=>openNew(+b.dataset.new)));
  box.querySelectorAll('[data-rev]').forEach(b=>b.addEventListener('click',()=>{const p=b.dataset.rev.split('|');openRevGroup(+p[0],+p[1]);}));
  box.querySelectorAll('[data-pt]').forEach(b=>b.addEventListener('click',()=>{const p=b.dataset.pt.split('|');if(p[2]==='n')openNew2(PLISTS[+p[1]]);else openPartCheck(+p[0],+p[1]);}));
  const ra=box.querySelector('[data-revall]');if(ra)ra.addEventListener('click',openRevAll);
  document.getElementById('chStart').addEventListener('click',()=>{const v=document.getElementById('startDate2').value;if(v){RV.start=v;save();renderDash();}});
  document.getElementById('resetBtn').addEventListener('click',()=>{if(confirm('确定清空全部复习进度（新学记录+复习轮次+检查标记）？生词本不受影响。')){RV={start:null,words:{},checks:{}};save();renderDash();}});
  document.getElementById('cdBox').addEventListener('click',e=>{if(e.target&&e.target.id==='cdGo')openRevAll();});
  const d2=document.getElementById('day2Btn');if(d2)d2.addEventListener('click',()=>openNew2([2*dn-1,2*dn]));
  startCD();
}
/* ---------- 复习倒计时 ticker ---------- */
function refreshRV(){try{const raw=JSON.parse(localStorage.getItem(SKEY)||'null');
  if(raw&&raw.words){RV=raw;if(!RV.checks)RV.checks={};Object.keys(RV.words).forEach(k=>{const st=RV.words[k];if(st&&st.t0===undefined)st.t0=st.t;});}}catch(e){}}
function tickCD(){
  const el=document.getElementById('cdBody');if(!el)return;
  refreshRV();
  const dd=dueData();
  let html2,key;
  if(dd.total>0){
    key='due'+dd.total;
    html2='<div class="cdurgent"><span class="cdn">🔔 '+dd.total+' 词已到期！</span><span style="color:#8a6d2b;font-size:13.5px">现在正是遗忘临界点，立刻复习效果最好</span><button class="btn o" id="cdGo" style="background:#e6a23c">▶ 立即开始复习</button></div>';
    if(lastDueSeen===0)beep();
    if(!titleInt)titleInt=setInterval(()=>{document.title=(document.title===origTitle?'🔔 有 '+lastDueSeen+' 词待复习！':origTitle);},1200);
  }else if(dd.up.length){
    const u=dd.up[0];const sec=Math.ceil(u.left/1000);
    key='up'+u.k+sec;
    html2='<div class="cdnext">下次复习：<b>List '+String(u.n).padStart(2,'0')+'</b> · 第'+(u.s+1)+'轮（'+LAB[u.s]+'）</div>'
      +'<div class="cdtime">'+fmtCD(u.left)+'</div>'
      +'<div class="cdlab">到点后本页会响铃提醒；在其它页面右下角也会弹出提醒</div>';
    if(titleInt){clearInterval(titleInt);titleInt=null;document.title=origTitle;}
  }else{
    key='none';
    html2='<div class="cdlab" style="font-size:14px">暂无排期——先在下方完成新学，学完后这里会自动开始倒计时。</div>';
    if(titleInt){clearInterval(titleInt);titleInt=null;document.title=origTitle;}
  }
  lastDueSeen=dd.total;
  if(key!==cdKey){cdKey=key;el.innerHTML=html2;}
}
function startCD(){if(!cdInt)cdInt=setInterval(tickCD,1000);cdKey='';tickCD();}
/* ---------- session ---------- */
const sess=document.getElementById('sess');
let S=null;
function wordOf(k){const p=k.split('/');return DATA.lists[+p[0]-1].words.find(w=>w.w===p[1]);}
function openNew(n){openNew2([n]);}
/* 连续学习会话：新词 + 每5分钟原地复习本周期词 + 每30分钟(按总计时)复习30分钟池，直到两个List学完，全部进12h队列 */
function openNew2(lists){
  const items=[];lists.forEach(n=>DATA.lists[n-1].words.forEach(w=>{const k=n+'/'+w.w;if(!RV.words[k])items.push({k,n,wd:w});}));
  if(!items.length){toast('这些 List 已全部学完');return;}
  S={mode:'new2',lists,queue:items,idx:0,again:[],cycle:[],bucket:[],doneCount:0,phase:'study',touched:[],total:items.length,pending30:false,finalFlush:false,n5:0,n30:0,study:null,label:''};
  startSess('📖 今日学习 · '+lists.map(n=>'List'+String(n).padStart(2,'0')).join('+'));
}
function openRevGroup(n,s){
  const keys=[];const now=Date.now();
  Object.keys(RV.words).forEach(k=>{const st=RV.words[k];const d0=nextDue(st);if(st.s===s&&d0!==null&&+k.split('/')[0]===n&&now>=d0)keys.push(k);});
  if(!keys.length){toast('该组没有到期词');renderDash();return;}
  S={mode:'rev',n,queue:shuffle(keys.map(k=>({k,n,wd:wordOf(k)}))),again:[],idx:0,total:keys.length,touched:[]};
  startSess('复习 · List '+String(n).padStart(2,'0')+' · '+LAB[s]);
}
function openRevAll(){
  const dd=dueData();const keys=[];dd.groups.forEach(g=>g.keys.forEach(k=>keys.push(k)));
  if(!keys.length){toast('没有到期词');return;}
  S={mode:'rev',n:0,queue:shuffle(keys.map(k=>({k,n:+k.split('/')[0],wd:wordOf(k)}))),again:[],idx:0,total:keys.length,touched:[]};
  startSess('复习 · 全部到期');
}
function startSess(label){
  document.getElementById('dashWrap').style.display='none';
  sess.style.display='block';
  S.label=label;
  S.sessStart=Date.now();
  if(S.mode==='new2'){S.cycleStart=S.sessStart;S.next30=S.sessStart+30*6e4;}
  setPhaseUI();
  if(S.timerInt)clearInterval(S.timerInt);
  S.timerInt=setInterval(()=>{
    const el=document.getElementById('cTimer');
    if(el&&S.cardStart)el.innerHTML='⏱ 思考中 <b>'+((Date.now()-S.cardStart)/1000).toFixed(1)+'</b> 秒';
  },100);
  if(S.tick2)clearInterval(S.tick2);
  S.tick2=setInterval(tickS2,1000);tickS2();
  renderCard();
}
function fmtHMS(ms){const s=Math.floor(ms/1000);const h=Math.floor(s/3600),m=Math.floor(s%3600/60),ss=s%60;
  return (h?h+':':'')+String(m).padStart(2,'0')+':'+String(ss).padStart(2,'0');}
function fmtMS(ms){const s=Math.max(0,Math.ceil(ms/1000));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');}
function setPhaseUI(){
  if(S.mode!=='new2'){sess.className='';document.getElementById('sMode').textContent=S.label;return;}
  sess.className=S.phase==='r5'?'ph-r5':(S.phase==='r30'?'ph-r30':'');
  document.getElementById('sMode').textContent=S.phase==='r5'?'🔄 5分钟周期复习':(S.phase==='r30'?'🔄 30分钟周期复习':S.label);
}
/* 总计时 & 周期倒计时（学习阶段每5分钟触发周期复习；总计时每30分钟触发30分钟池复习） */
function tickS2(){
  if(!S)return;
  const now=Date.now();
  const elT=document.getElementById('sTotalT');if(elT)elT.textContent=fmtHMS(now-S.sessStart);
  if(S.mode!=='new2')return;
  const elC=document.getElementById('sCycleT');
  const elP=document.getElementById('sPools');
  if(elP)elP.textContent='5分钟周期池 '+S.cycle.length+' 词 · 30分钟池 '+S.bucket.length+' 词 · 已入12h队列 '+S.doneCount+' 词';
  if(S.phase==='study'){
    const left=5*6e4-(now-S.cycleStart);
    if(elC)elC.textContent=left>0?fmtMS(left):'00:00';
    if(left<=0){
      if(S.cycle.length){startReview('5');return;}
      S.cycleStart=now;
    }
    if(now>=S.next30){S.next30+=30*6e4;if(S.bucket.length){startReview('30');return;}}
  }else{
    if(elC)elC.textContent='复习中';
    if(now>=S.next30){S.next30+=30*6e4;if(S.bucket.length)S.pending30=true;}
  }
}
function startReview(kind){
  const qm=document.getElementById('quizMask');if(qm)qm.classList.remove('show');
  if(S.phase==='study')S.study={queue:S.queue,idx:S.idx,again:S.again};
  S.phase=kind==='5'?'r5':'r30';
  S.queue=shuffle((kind==='5'?S.cycle:S.bucket).slice());
  S.idx=0;S.again=[];
  setPhaseUI();
  toast(kind==='5'?'⏰ 5分钟到了！原地复习本周期 '+S.queue.length+' 词':'⏰ 30分钟到了！复习30分钟池 '+S.queue.length+' 词');
  renderCard();
}
function endReview(kind){
  if(kind==='r5'){S.n5++;toast('✅ 5分钟周期复习完成 · 单词已放入30分钟周期池');}
  else{S.n30++;toast('✅ 30分钟复习完成 · 这些词今天搞定，12小时后见');}
  if(S.pending30&&S.bucket.length){S.pending30=false;startReview('30');return;}
  if(S.finalFlush){checkFinish();return;}
  S.phase='study';S.cycleStart=Date.now();
  S.queue=S.study.queue;S.idx=S.study.idx;S.again=S.study.again;
  setPhaseUI();renderCard();
}
function checkFinish(){
  if(S.cycle.length){startReview('5');return;}
  if(S.bucket.length){startReview('30');return;}
  renderDone();
}
function exitSess(){if(S){if(S.timerInt)clearInterval(S.timerInt);if(S.tick2)clearInterval(S.tick2);}S=null;sess.className='';sess.style.display='none';document.getElementById('dashWrap').style.display='';if('speechSynthesis' in window)speechSynthesis.cancel();renderDash();}
document.getElementById('sExit').addEventListener('click',exitSess);
function sentHtml(en,target){
  return en.split(/(\[\[[^\[\]]+?\]\])/).map(p=>{
    if(!p.startsWith('[['))return esc(p);
    const form=p.slice(2,-2);
    let low=form.toLowerCase().replace(/’/g,"'").replace(/‑/g,'-');
    const hit=low===target||lemmas(low).has(target);
    return hit?'<mark class="thl">'+esc(form)+'</mark>':esc(form);
  }).join('');
}
function renderCard(){
  const cb=document.getElementById('cardBox');
  if(S.idx>=S.queue.length){
    if(S.again.length){S.queue=shuffle(S.again);S.again=[];S.idx=0;return renderCard();}
    if(S.mode==='new2'){
      if(S.phase==='study'){S.finalFlush=true;return checkFinish();}
      return endReview(S.phase);
    }
    return renderDone();
  }
  if(S.mode==='new2'&&S.phase==='study'){
    const learned=S.total-(S.queue.length-S.idx);
    document.getElementById('sProg').textContent='📖 新学中 · 还剩 '+(S.queue.length-S.idx)+' 词 · 已学 '+learned+'/'+S.total;
    document.getElementById('sBarFill').style.width=Math.round(learned/S.total*100)+'%';
  }else{
    document.getElementById('sProg').textContent='第 '+(S.idx+1)+' / '+S.queue.length+' 张'+(S.again.length?' · 待再过 '+S.again.length+' 词':'');
    document.getElementById('sBarFill').style.width=Math.round(S.idx/S.queue.length*100)+'%';
  }
  const it=S.queue[S.idx];const w=it.wd;
  S.cardStart=Date.now();S.answered=false;
  let back='<div class="cdef">'+esc(w.def||'')+'</div>';
  if(w.r)back+='<div class="croot">🌱 '+esc(w.r)+'</div>';
  (w.si||[]).forEach(si=>{const s=DATA.lists[it.n-1].sents[si];
    back+='<div class="cex"><div class="en">'+sentHtml(s.en,w.w.toLowerCase())+'</div><div class="zh">'+esc(s.zh)+'</div></div>';});
  if(!(w.si||[]).length)back+='<div class="cex"><div class="zh">本词短文中暂无例句</div></div>';
  cb.innerHTML='<div class="card" id="fcard">'
    +'<div class="cfront">'
    +'<div class="ctimer" id="cTimer">⏱ 思考中 <b>0.0</b> 秒</div>'
    +'<div class="cw">'+esc(w.w)+'</div><div class="cph">'+esc(w.phon||'')+'</div>'
    +'<button class="csp" id="csp">🔊 朗读</button>'
    +'<div class="flipHint">先回忆释义，再选择熟悉程度</div>'
    +'<div class="cbtns"><button id="bNo">😵 不认识</button><button id="bMid">🤔 模糊</button><button id="bQuiz">✅ 认识</button><button id="bYes">💯 完全认识</button></div>'
    +'</div>'
    +'<div class="cback">'+back
    +'<div class="cused">⏱ 用时 <span id="usedT">0.0</span> 秒</div>'
    +'<div class="kbd">快捷键：1 不认识 · 2 模糊 · 3 认识（4选1） · 4 完全认识 · 空格/回车 继续</div>'
    +'<button class="cnext" id="cNext">继续 →</button>'
    +'</div></div>';
  document.getElementById('csp').addEventListener('click',e=>{e.stopPropagation();speak(w.w);});
  function pick(a){
    if(S.answered)return;S.answered=true;
    const elapsed=((Date.now()-S.cardStart)/1000);
    document.getElementById('fcard').classList.add('flip');
    document.getElementById('usedT').textContent=elapsed.toFixed(1);
    ['bNo','bMid','bQuiz','bYes'].forEach(id=>{const b=document.getElementById(id);if(b)b.disabled=true;});
    if(a==='quiz')openQuiz();
    else answer(a,false);
  }
  document.getElementById('bNo').addEventListener('click',()=>pick('no'));
  document.getElementById('bMid').addEventListener('click',()=>pick('mid'));
  document.getElementById('bQuiz').addEventListener('click',()=>pick('quiz'));
  document.getElementById('bYes').addEventListener('click',()=>pick('yes'));
  document.getElementById('cNext').addEventListener('click',()=>{S.idx++;renderCard();});
}
function answer(a,advance){
  const it=S.queue[S.idx];const now=Date.now();
  if(S.mode==='new2'){
    if(S.phase==='study'){
      const old=RV.words[it.k];
      RV.words[it.k]={t0:(old&&old.t0)||now,t:now,s:0};
      if(a==='no')S.again.push(it);else S.cycle.push(it);
    }else if(S.phase==='r5'){
      const st=RV.words[it.k];st.t=now;
      if(a==='no'){S.again.push(it);}
      else{
        st.s=1;
        const ci=S.cycle.findIndex(x=>x.k===it.k);
        if(ci>=0){S.cycle.splice(ci,1);S.bucket.push(it);}
        if(a==='mid')S.again.push(it);
      }
    }else{ /* r30 */
      const st=RV.words[it.k];st.t=now;
      if(a==='no'){S.again.push(it);}
      else{
        st.s=2;
        const bi=S.bucket.findIndex(x=>x.k===it.k);
        if(bi>=0){S.bucket.splice(bi,1);S.doneCount++;}
        if(a==='mid')S.again.push(it);
      }
    }
    S.touched.push(it.k);save();
    if(advance){S.idx++;renderCard();}
    return;
  }
  if(S.mode==='new'){
    const old=RV.words[it.k];
    RV.words[it.k]={t0:(old&&old.t0)||now,t:now,s:0};
    if(a==='no')S.again.push(it);
  }else{
    const st=RV.words[it.k];st.t=now;
    if(a==='yes')st.s=Math.min(8,st.s+1);
    else if(a==='mid'){st.s=Math.min(8,st.s+1);S.again.push(it);}
    else{st.s=0;S.again.push(it);}
  }
  S.touched.push(it.k);
  save();
  if(advance){S.idx++;renderCard();}
}
/* ---------- 4-choice quiz on "认识" ---------- */
function openQuiz(){
  const it=S.queue[S.idx];const w=it.wd;
  const opts=[{t:true,def:w.def||''}];
  (w.dists||[]).forEach(pi=>{if(POOL[pi])opts.push({t:false,def:POOL[pi].def||''});});
  while(opts.length<4)opts.push({t:false,def:POOL[Math.floor(Math.random()*POOL.length)].def||''});
  shuffle(opts);
  const mask=document.getElementById('quizMask');
  mask.innerHTML='<div class="qbox"><div class="qh">请选出正确释义 · 来自 3 个拼写相似词的干扰项</div>'
    +'<div class="qw">'+esc(w.w)+'</div><div class="qph">'+esc(w.phon||'')+'</div>'
    +'<div class="qask">以下哪一个是 <b>'+esc(w.w)+'</b> 的中文意思？</div>'
    +'<div class="qopts">'+opts.map((o,i)=>'<div class="qopt" data-i="'+i+'">'+String.fromCharCode(65+i)+'. '+esc(o.def)+'</div>').join('')+'</div>'
    +'<div class="qfb" id="qfb"></div></div>';
  mask.classList.add('show');
  let answered=false;
  mask.querySelectorAll('.qopt').forEach(el=>{
    el.addEventListener('click',()=>{
      if(answered)return;answered=true;
      const i=+el.dataset.i;const correct=opts[i].t;
      const fb=document.getElementById('qfb');
      if(correct){el.classList.add('correct');fb.textContent='✅ 回答正确，已进入下一轮';fb.className='qfb ok';
        setTimeout(()=>{mask.classList.remove('show');if(S&&S.queue[S.idx]===it)answer('yes',false);},650);}
      else{el.classList.add('wrong');
        mask.querySelectorAll('.qopt').forEach(x=>{if(opts[+x.dataset.i].t)x.classList.add('correct');x.classList.add('disabled');});
        fb.textContent='❌ 答错了，正确答案已标绿，本轮再过一次';fb.className='qfb no';
        setTimeout(()=>{mask.classList.remove('show');if(S&&S.queue[S.idx]===it)answer('mid',false);},1100);}
    });
  });
}
function renderDone(){
  if(S.timerInt)clearInterval(S.timerInt);
  /* 整轮完成：本轮所有作答词的「重新计时基准」统一更新为现在（5分钟/30分钟轮次的相对计时起点） */
  const rnow=Date.now();S.touched.forEach(k=>{const st=RV.words[k];if(st)st.t=rnow;});
  if(S.checkKey){RV.checks[S.checkKey]=rnow;}
  save();
  document.getElementById('sBarFill').style.width='100%';
  document.getElementById('sProg').textContent='本轮完成';
  const totalSec=(Date.now()-S.sessStart)/1000;
  const mm=Math.floor(totalSec/60),ss=Math.round(totalSec%60);
  const avg=(totalSec/S.total).toFixed(1);
  const timeLine='<p>⏱ 本轮总用时 <b>'+(mm?mm+'分':'')+ss+'秒</b> · 共 <b>'+S.total+'</b> 词 · 平均 <b>'+avg+'</b> 秒/词</p>';
  let msg='';
  if(S.mode==='new2'){
    msg='<p><b>'+S.lists.map(n=>'List '+String(n).padStart(2,'0')).join(' + ')+'</b> 全部拿下！</p>'
      +timeLine
      +'<p>新学 <b>'+S.total+'</b> 词 · 过程中完成 5分钟周期复习 <b>'+S.n5+'</b> 轮 · 30分钟周期复习 <b>'+S.n30+'</b> 轮</p>'
      +'<p>📦 全部单词已进入「<b>12小时后</b>」复习队列——按首次学习总时间计算，到点本页响铃提醒，之后按 1天 → 2天 → 4天 → 7天 → 15天 推进。</p>';
  }else if(S.mode==='new'){
    msg='<p><b>List '+String(S.n).padStart(2,'0')+'</b> 新学完成，'+S.total+' 词已进入记忆周期。</p>'
      +timeLine
      +'<p>⏰ 5 分钟倒计时已从现在开始，到点会响铃提醒（在其它页面右下角也会弹出提醒）。<br>之后：30分钟（按本轮完成重新计时）→ 12小时起按首次学习总时间推进 1天 / 2天 / 4天 / 7天 / 15天。</p>'
      +'<p class="muted">建议现在顺手读一遍对应埋词短文加深印象：List'+String(S.n).padStart(2,'0')+'.html</p>';
  }else{
    msg='<p>本轮 <b>'+S.total+'</b> 词复习完成！下一轮倒计时已从现在开始重新计时。</p>'+timeLine+'<p class="muted">12小时及以后的轮次按首次学习总时间计算；未到期的词会在计划页显示倒计时。</p>';
  }
  document.getElementById('cardBox').innerHTML='<div class="done"><h2>🎉 本轮完成</h2>'+msg+'<div style="margin-top:18px;display:flex;gap:10px;justify-content:center"><button class="btn" id="doneBack">返回计划页</button>'
    +(BACK?'<button class="btn g" id="doneRet">← 返回 '+esc(BACK)+'</button>':'')+'</div></div>';
  document.getElementById('doneBack').addEventListener('click',exitSess);
  if(BACK)document.getElementById('doneRet').addEventListener('click',()=>{location.href=BACK;});
}
document.addEventListener('keydown',e=>{
  if(!S||sess.style.display==='none')return;
  if(e.key===' '||e.key==='Enter'){
    e.preventDefault();
    const card=document.getElementById('fcard');
    if(card&&card.classList.contains('flip')){S.idx++;renderCard();}
    return;
  }
  const map={'1':'bNo','2':'bMid','3':'bQuiz','4':'bYes'};
  if(map[e.key]){const b=document.getElementById(map[e.key]);if(b&&!b.disabled)b.click();}
  if(e.key==='Escape'){const m=document.getElementById('quizMask');if(m.classList.contains('show'))m.classList.remove('show');else exitSess();}
});
setInterval(()=>{if(!S&&sess.style.display==='none'&&RV.start)renderDash();},30000);
renderDash();
"""

review_html = ("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>每日复习计划 · 艾宾浩斯遗忘曲线 · 十天搞定考研词汇</title>
<style>__CSS__</style>
</head>
<body>
<div class="wrap" id="dashWrap">
  <div class="top">
    <h1>📅 每日复习计划 · 艾宾浩斯遗忘曲线</h1>
    <div><a href="index.html">← 返回短文目录</a><a href="roots.html">🌱 词根中心</a></div>
  </div>
  <div id="dash"></div>
</div>
<div id="sess" style="display:none">
  <div class="sess-top">
    <button id="sExit">✕ 退出本轮</button>
    <div class="sprog" id="sProg"></div>
    <div class="smode" id="sMode"></div>
  </div>
  <div class="shead"><span>🕒 总计时 <b id="sTotalT">00:00</b></span><span>⏳ 5分钟周期 <b id="sCycleT">05:00</b></span><span id="sPools"></span></div>
  <div class="sbar"><div id="sBarFill"></div></div>
  <div id="cardBox"></div>
</div>
<div id="quizMask"></div>
<div id="toast"></div>
<script>
__JS__
</script>
</body>
</html>
""").replace('__CSS__', REVIEW_CSS).replace('__JS__', REVIEW_JS.replace('__RVDATA__', RV_DATA_JSON))
open(os.path.join(ROOT, 'review.html'), 'w', encoding='utf-8').write(review_html)
print('review.html built: lists=%d total=%d' % (len(rv_lists), sum(len(l['words']) for l in rv_lists)))

# ---------------------------------------------------------------- index
cards = []
for m in meta:
    cards.append(f"""<a class="card" href="List{m['n']:02d}.html" data-n="{m['n']}">
  <h2>List {m['n']} <span style="font-size:13px;color:#8a96a5;font-weight:normal;">Day {m['day']}</span></h2>
  <span class="tag">{html.escape(m['cat'])}</span>
  <div class="nums">词表 {m['nwords']} 词 · {m['nsents']} 句精读 · 拓展 {m['nextra']} · 长难句 {m['ngram']}</div>
  <div class="pwrap"><div class="pbar"></div></div><div class="pct"></div>
</a>""")

index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>十天搞定考研词汇 · 3502 词短文精读</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <h1>十天搞定考研词汇 · 埋词短文精读 20 篇</h1>
    <p>3502 个考纲词逐词埋入考研级短文 · 逐句中英对译 · 长难句语法拆解 · 悬停/点击查词朗读 · 生词卡片复习</p>
    <p style="margin-top:14px"><a href="roots.html" style="display:inline-block;background:linear-gradient(90deg,#1c9e63,#2bb673);color:#fff;text-decoration:none;padding:11px 30px;border-radius:24px;font-size:15px;box-shadow:0 6px 18px rgba(28,158,99,.3)">🌱 进入 60 词根学习中心 · 408 词适用词根法 / 3094 词整体记忆</a></p>
    <p style="margin-top:12px"><a href="review.html" style="display:inline-block;background:linear-gradient(90deg,#2b7cdd,#56a3f0);color:#fff;text-decoration:none;padding:11px 30px;border-radius:24px;font-size:15px;box-shadow:0 6px 18px rgba(43,124,221,.3)">📅 进入每日复习计划 · 艾宾浩斯遗忘曲线 10 天背完 3502 词</a></p>
  </div>
  <div class="grid">
{chr(10).join(cards)}
  </div>
  <div class="legend">
    <b>功能说明：</b><br>
    ① <span class="dot-l">蓝色虚线词</span>＝本 List 词表单词（每词恰好出现一次），<span class="dot-e">绿色虚线词</span>＝标注的超纲拓展词与短语；其余所有单词也都可以<b>悬停</b>，支持 🔊 朗读 / 跳转有道词典。<br>
    ② 三种阅读模式：<b>英文沉浸</b>（悬停句子看译文）、<b>逐句对照</b>、<b>仅看中文</b>；字号、英音/美音可切换。<br>
    ③ 句首工具条：🔊 朗读整句、「译」临时显示译文；标有 🔷 的句子是<b>长难句</b>，点击可展开成分拆解 + 语法考点 + 翻译要点，顶部「长难句」按钮可一键展开全部。<br>
    ④ 点击单词加入右侧「📓 生词队列」（自动本地保存、20 篇共享），支持复制导出与 🃏 <b>闪卡复习</b>（翻面看释义、已掌握自动移除）。<br>
    ⑤ 阅读进度自动记录，读完 95% 自动标记 ✓，目录卡片可查看每篇进度。<br>
    ⑥ 🌱 <b><a href="roots.html" style="color:#138a55">词根学习中心</a></b>：3502 词分两大类——可按 60 个核心词根拆解的 408 词（文中带 <sup class="rb">根</sup> 角标，悬停看「前缀+词根→字面义」，顶栏可一键聚焦）和不适用词根法、需整体记忆的 3094 词；支持任意单词查分类。<br>
    ⑦ 📅 <b><a href="review.html" style="color:#1f66c2">每日复习计划</a></b>：按艾宾浩斯遗忘曲线 10 天背完全部 3502 词——每天新学 2 个 List，每词自动在 <b>5分钟 / 30分钟 / 12小时 / 1天 / 2天 / 4天 / 7天 / 15天</b> 共 8 个遗忘临界点提醒复习；背词卡片自动摘取该词所在的短文例句（含中文译文与词根拆解）；每轮完成后自动重新倒计时，到点响铃提醒，在任何页面右下角都会弹出「去复习」提醒。
  </div>
</div>
<script>
document.querySelectorAll('.card').forEach(c=>{{
  const n=String(c.dataset.n).padStart(2,'0');
  const v=parseFloat(localStorage.getItem('ky_read_'+n)||'0');
  c.querySelector('.pbar').style.width=Math.round(v*100)+'%';
  c.querySelector('.pct').textContent=v>=1?'100%':Math.round(v*100)+'%';
  if(v>=1)c.classList.add('done');
}});
</script>
</body>
</html>
"""
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(
    index_html.replace('</script>\n</body>', REVIEW_BELL_JS + '\n</script>\n</body>'))
print('index.html built')
print('TOTAL list words:', sum(m['nwords'] for m in meta),
      '| sentences:', sum(m['nsents'] for m in meta),
      '| extra:', sum(m['nextra'] for m in meta),
      '| grammar:', sum(m['ngram'] for m in meta))
