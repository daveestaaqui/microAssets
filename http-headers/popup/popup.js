
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'http_headers_viewer';
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

document.getElementById('fetchBtn').onclick=function(){
var el=document.getElementById('headers');
el.innerHTML='<span style="color:#facc15;">Loading…</span>';
chrome.tabs.query({active:true,currentWindow:true},function(tabs){
var url=tabs[0].url;
fetch(url,{method:'HEAD',mode:'no-cors'}).then(function(r){
var html='<div style="padding:4px;margin-bottom:4px;border-radius:4px;background:rgba(168,85,247,0.1);color:#c084fc;">'+url.slice(0,50)+'</div>';
r.headers.forEach(function(v,k){
var color='#d4d4d8';
if(k.includes('security')||k.includes('strict')||k.includes('x-frame'))color='#4ade80';
if(k.includes('server')||k.includes('powered'))color='#fbbf24';
html+='<div style="padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.03);"><span style="color:#a855f7;font-weight:600;">'+k+'</span>: <span style="color:'+color+';">'+v+'</span></div>';
});
if(html.indexOf('span style="color:#a855f7')===-1||html.split('span style="color:#a855f7').length<3){
html+='<div style="margin-top:8px;padding:4px;border-radius:4px;background:rgba(251,191,36,0.1);color:#fbbf24;font-size:9px;">⚠️ Some headers hidden by CORS. Open DevTools Network tab for full headers.</div>';}
el.innerHTML=html;
}).catch(function(e){
el.innerHTML='<span style="color:#f87171;">Error: '+e.message+'</span>';});});};
