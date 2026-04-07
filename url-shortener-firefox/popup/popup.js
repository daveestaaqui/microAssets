
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'url_shortener_and_qr_generator';
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

document.getElementById('shortenBtn').onclick=async()=>{const url=document.getElementById('url').value.trim();if(!url)return;
try{const r=await fetch('https://tinyurl.com/api-create.php?url='+encodeURIComponent(url));const short=await r.text();
document.getElementById('short').value=short;document.getElementById('result').style.display='block';
chrome.storage.local.get(['urlHistory'],(d)=>{const h=d.urlHistory||[];h.unshift({original:url,short,ts:Date.now()});if(h.length>20)h.length=20;chrome.storage.local.set({urlHistory:h},renderHistory);});
}catch(e){document.getElementById('short').value='Error: '+e.message;document.getElementById('result').style.display='block';}};
document.getElementById('short').onclick=function(){navigator.clipboard.writeText(this.value).then(()=>{const o=this.value;this.value='✅ Copied!';setTimeout(()=>this.value=o,1200);});};
function renderHistory(){chrome.storage.local.get(['urlHistory'],(d)=>{const h=d.urlHistory||[];const el=document.getElementById('history');el.innerHTML=h.map(i=>'<div style="padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.03);cursor:pointer;" onclick="navigator.clipboard.writeText(\''+i.short+'\')"><span style="color:#71717a;">'+i.original.slice(0,30)+'…</span> → <span style="color:#4ade80;">'+i.short+'</span></div>').join('');});}
renderHistory();
