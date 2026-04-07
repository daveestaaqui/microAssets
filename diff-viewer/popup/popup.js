
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'text_diff_viewer';
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

document.getElementById('diffBtn').onclick=function(){
var a=document.getElementById('textA').value.split('\n');
var b=document.getElementById('textB').value.split('\n');
var maxLen=Math.max(a.length,b.length);
var html='';var adds=0,dels=0,same=0;
for(var i=0;i<maxLen;i++){
var la=a[i]||'';var lb=b[i]||'';
if(la===lb){html+='<div style="padding:1px 4px;color:#71717a;">'+(i+1)+' &nbsp;'+la.replace(/</g,'&lt;')+'</div>';same++;}
else{if(la){html+='<div style="padding:1px 4px;background:rgba(239,68,68,0.1);color:#fca5a5;">- '+la.replace(/</g,'&lt;')+'</div>';dels++;}
if(lb){html+='<div style="padding:1px 4px;background:rgba(74,222,128,0.1);color:#86efac;">+ '+lb.replace(/</g,'&lt;')+'</div>';adds++;}}}
html='<div style="padding:4px;margin-bottom:4px;border-radius:4px;background:rgba(255,255,255,0.02);font-size:10px;"><span style="color:#4ade80;">+'+adds+'</span> <span style="color:#f87171;">-'+dels+'</span> <span style="color:#71717a;">'+same+' unchanged</span></div>'+html;
document.getElementById('result').innerHTML=html;};
