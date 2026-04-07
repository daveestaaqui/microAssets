
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'robotstxt_viewer';
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

document.getElementById('loadBtn').onclick=function(){
var el=document.getElementById('content');
el.textContent='Loading…';
chrome.tabs.query({active:true,currentWindow:true},function(tabs){
var url=new URL(tabs[0].url);
var robotsUrl=url.origin+'/robots.txt';
fetch(robotsUrl).then(function(r){return r.text();}).then(function(text){
var lines=text.split('\n');
var html='';
lines.forEach(function(line){
var trimmed=line.trim();
if(trimmed.startsWith('#'))html+='<span style="color:#52525b;">'+line+'</span>\n';
else if(trimmed.toLowerCase().startsWith('user-agent'))html+='<span style="color:#a855f7;font-weight:bold;">'+line+'</span>\n';
else if(trimmed.toLowerCase().startsWith('disallow'))html+='<span style="color:#f87171;">'+line+'</span>\n';
else if(trimmed.toLowerCase().startsWith('allow'))html+='<span style="color:#4ade80;">'+line+'</span>\n';
else if(trimmed.toLowerCase().startsWith('sitemap'))html+='<span style="color:#60a5fa;">'+line+'</span>\n';
else html+=line+'\n';
});
el.innerHTML='<div style="margin-bottom:4px;padding:3px;border-radius:4px;background:rgba(168,85,247,0.1);color:#c084fc;font-size:9px;">'+robotsUrl+'</div>'+html;
}).catch(function(e){
el.innerHTML='<span style="color:#f87171;">No robots.txt found at '+robotsUrl+'</span>';});});};
