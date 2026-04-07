
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'seo_content_analyzer_pro';
  const USAGE_KEY = EXT_ID + '_usage';

  // Track usage
  _api.storage.local.get([USAGE_KEY], (r) => {
    const count = ((r && r[USAGE_KEY]) || 0) + 1;
    _api.storage.local.set({ [USAGE_KEY]: count });
    // Show feedback prompt after 3 uses
    if (count >= 3) {
      const fb = document.getElementById('ma-feedback');
      if (fb) fb.style.display = 'block';
    }
  });

  // Wire up rate link
  // Smart Review Gate: Two-step satisfaction filter
  const rateLink = document.getElementById('ma-rate');
  if (rateLink) {
    rateLink.addEventListener('click', (e) => {
      e.preventDefault();
      const happy = confirm('Are you enjoying this extension? \n\nClick OK if yes, Cancel to send us feedback instead.');
      if (happy) {
        // Happy path → CWS review page
        try {
          const id = (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime.id : chrome.runtime.id;
          window.open('https://chrome.google.com/webstore/detail/' + id + '/reviews', '_blank');
        } catch(err) {
          window.open('https://chromewebstore.google.com/search/OmniSuite', '_blank');
        }
      } else {
        // Unhappy path → private feedback (funneled to AI support agent)
        window.open('mailto:support@sporlyworks.com?subject=Extension Feedback', '_blank');
      }
    });
  }

  // Global error handler
  window.addEventListener('error', (e) => {
    _api.storage.local.get(['ma_errors'], (r) => {
      const errors = (r && r.ma_errors) || [];
      errors.push({ ext: EXT_ID, msg: e.message, ts: Date.now() });
      if (errors.length > 20) errors.shift();
      _api.storage.local.set({ ma_errors: errors });
    });
  });
})();

let uses=0;
document.getElementById('analyzeBtn').onclick=()=>{chrome.storage.local.get(['omnisuite_pro_key_seo-content-pro'],d=>{uses++;if(uses>3&&!d['omnisuite_pro_key_seo-content-pro']){document.getElementById('gate').style.display='block';return;}
chrome.tabs.query({active:true,currentWindow:true},tabs=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:()=>{const text=document.body.innerText;const words=text.split(/\s+/).filter(w=>w.length>0);const sentences=text.split(/[.!?]+/).filter(s=>s.trim().length>0);const h1s=document.querySelectorAll('h1');const h2s=document.querySelectorAll('h2');const h3s=document.querySelectorAll('h3');const imgs=document.querySelectorAll('img');const imgsNoAlt=Array.from(imgs).filter(i=>!i.alt||i.alt.trim()==='');const links=document.querySelectorAll('a[href]');const internal=Array.from(links).filter(l=>l.hostname===location.hostname);const external=Array.from(links).filter(l=>l.hostname!==location.hostname&&l.hostname);const meta=document.querySelector('meta[name=description]');const title=document.title;const canonical=document.querySelector('link[rel=canonical]');const avgWordsPerSentence=words.length/Math.max(sentences.length,1);const readability=avgWordsPerSentence<15?'A':avgWordsPerSentence<20?'B':avgWordsPerSentence<25?'C':'F';
const wordFreq={};words.forEach(w=>{const lw=w.toLowerCase().replace(/[^a-z]/g,'');if(lw.length>3)wordFreq[lw]=(wordFreq[lw]||0)+1;});
const topWords=Object.entries(wordFreq).sort((a,b)=>b[1]-a[1]).slice(0,10);
return{wordCount:words.length,sentenceCount:sentences.length,h1Count:h1s.length,h2Count:h2s.length,h3Count:h3s.length,imgCount:imgs.length,imgsNoAlt:imgsNoAlt.length,internalLinks:internal.length,externalLinks:external.length,metaDesc:meta?.content||'',metaDescLen:meta?.content?.length||0,titleLen:title.length,title,hasCanonical:!!canonical,readability,avgWordsPerSentence:Math.round(avgWordsPerSentence),topWords};}}).then(r=>{const d=r[0].result;const el=document.getElementById('results');
const score=(d.h1Count===1?15:0)+(d.metaDescLen>120&&d.metaDescLen<160?15:d.metaDescLen>0?8:0)+(d.titleLen>30&&d.titleLen<60?15:d.titleLen>0?8:0)+(d.imgsNoAlt===0?10:0)+(d.wordCount>300?10:d.wordCount>150?5:0)+(d.readability<='B'?10:5)+(d.hasCanonical?10:0)+(d.internalLinks>2?10:5)+(d.externalLinks>0?5:0);
const grade=score>=80?{l:'A',c:'#4ade80'}:score>=60?{l:'B',c:'#facc15'}:score>=40?{l:'C',c:'#fb923c'}:{l:'F',c:'#f87171'};
el.innerHTML=`<div style="text-align:center;margin-bottom:10px;"><span style="font-size:40px;font-weight:bold;color:${grade.c};">${grade.l}</span><span style="font-size:14px;color:#a1a1aa;margin-left:4px;">${score}/100</span></div>`+
[['📝 Word Count',d.wordCount],['📖 Sentences',d.sentenceCount],['📊 Readability',d.readability+' (avg '+d.avgWordsPerSentence+' words/sentence)'],['🏷️ Title ('+d.titleLen+' chars)',d.title.slice(0,50)],['📋 Meta Desc ('+d.metaDescLen+' chars)',d.metaDesc.slice(0,60)||'❌ Missing'],['📌 H1 Tags',d.h1Count+(d.h1Count===1?' ✅':d.h1Count===0?' ❌ Missing':' ⚠️ Multiple')],['📌 H2/H3 Tags',d.h2Count+'/'+d.h3Count],['🖼️ Images',d.imgCount+(d.imgsNoAlt>0?' ('+d.imgsNoAlt+' missing alt)':' ✅')],['🔗 Internal Links',d.internalLinks],['🌐 External Links',d.externalLinks],['🔗 Canonical',d.hasCanonical?'✅ Set':'❌ Missing']
].map(([k,v])=>`<div class="metric"><span class="metric-label">${k}</span><span class="metric-value">${v}</span></div>`).join('')+
'<h4 style="color:#c084fc;font-size:11px;margin:8px 0 4px;">Top Keywords</h4>'+d.topWords.map(([w,c])=>`<span style="display:inline-block;padding:2px 6px;margin:1px;border-radius:4px;background:rgba(168,85,247,0.15);color:#c084fc;font-size:10px;">${w} (${c})</span>`).join('');
});});});};
document.getElementById('actBtn')?.addEventListener('click',()=>{const k=document.getElementById('key').value.trim();if(k.length>=8){chrome.storage.local.set({'omnisuite_pro_key_seo-content-pro':k});document.getElementById('gate').style.display='none';}});
