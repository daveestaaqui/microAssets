
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'whois_and_dns_lookup';
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

document.getElementById('lookupBtn').onclick=function(){
var el=document.getElementById('result');
el.innerHTML='<span style="color:#facc15;">Looking up…</span>';
chrome.tabs.query({active:true,currentWindow:true},function(tabs){
var url=new URL(tabs[0].url);
var domain=url.hostname;
// Use DNS-over-HTTPS for DNS lookup
fetch('https://dns.google/resolve?name='+domain+'&type=A').then(function(r){return r.json();}).then(function(dns){
var html='<div style="padding:4px;margin-bottom:6px;border-radius:4px;background:rgba(168,85,247,0.1);color:#c084fc;font-weight:bold;">'+domain+'</div>';
html+='<div style="padding:3px 0;"><span style="color:#a855f7;">Status:</span> <span style="color:#4ade80;">'+dns.Status+' ('+(['NOERROR','FORMERR','SERVFAIL','NXDOMAIN'][dns.Status]||'Unknown')+')</span></div>';
if(dns.Answer){
dns.Answer.forEach(function(a){
var types={1:'A',5:'CNAME',28:'AAAA',15:'MX',16:'TXT',2:'NS'};
html+='<div style="padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.03);"><span style="color:#7dd3fc;">'+(types[a.type]||a.type)+'</span> <span style="color:#d4d4d8;">'+a.data+'</span> <span style="color:#52525b;font-size:9px;">TTL:'+a.TTL+'</span></div>';
});}
// Also fetch AAAA, MX, NS, TXT
var promises=['AAAA','MX','NS','TXT'].map(function(t){
return fetch('https://dns.google/resolve?name='+domain+'&type='+t).then(function(r){return r.json();});
});
Promise.all(promises).then(function(results){
results.forEach(function(r){if(r.Answer){r.Answer.forEach(function(a){
var types={1:'A',5:'CNAME',28:'AAAA',15:'MX',16:'TXT',2:'NS'};
html+='<div style="padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.03);"><span style="color:#7dd3fc;">'+(types[a.type]||a.type)+'</span> <span style="color:#d4d4d8;word-break:break-all;">'+a.data+'</span></div>';
});}});
el.innerHTML=html;
});
}).catch(function(e){el.innerHTML='<span style="color:#f87171;">Error: '+e.message+'</span>';});});};
