
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'broken_link_checker';
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

document.getElementById('scanBtn').onclick=()=>{document.getElementById('status').innerHTML='<span style="color:#facc15;">⏳ Scanning links…</span>';
chrome.tabs.query({active:true,currentWindow:true},tabs=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:()=>{const links=Array.from(document.querySelectorAll('a[href]')).map(a=>({href:a.href,text:a.textContent.trim().slice(0,30)||a.href.slice(0,30)})).filter(l=>l.href.startsWith('http'));return links;}}).then(async r=>{const links=r[0].result;const st=document.getElementById('status');const el=document.getElementById('results');st.textContent=`Checking ${links.length} links…`;el.textContent = '';let checked=0,broken=0;
for(const link of links.slice(0,50)){try{const r=await fetch(link.href,{method:'HEAD',mode:'no-cors',signal:AbortSignal.timeout(5000)});checked++;const ok=r.status===0||r.status<400;if(!ok)broken++;el.innerHTML+=`<div style="padding:3px;border-bottom:1px solid rgba(255,255,255,0.03);"><span style="color:${ok?'#4ade80':'#f87171'};">${ok?'✅':'❌'}</span> <span style="color:#d4d4d8;">${link.text}</span> <span style="color:#71717a;font-size:9px;">${link.href.slice(0,40)}…</span></div>`;st.textContent=`Checked ${checked}/${links.length} — ${broken} broken`;}catch(e){checked++;el.innerHTML+=`<div style="padding:3px;border-bottom:1px solid rgba(255,255,255,0.03);"><span style="color:#facc15;">⚠️</span> <span style="color:#d4d4d8;">${link.text}</span> <span style="color:#71717a;font-size:9px;">Timeout/CORS</span></div>`;}}
st.innerHTML=`<span style="color:${broken?'#f87171':'#4ade80'};">${broken?'❌ '+broken+' broken links found':'✅ All '+checked+' links OK!'}</span>`;});});};
