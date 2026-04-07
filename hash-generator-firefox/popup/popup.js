
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'hash_generator';
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

var input=document.getElementById('input'),results=document.getElementById('results');
async function hashText(algo,text){
var enc=new TextEncoder().encode(text);
var buf=await crypto.subtle.digest(algo,enc);
return Array.from(new Uint8Array(buf)).map(function(b){return b.toString(16).padStart(2,'0');}).join('');
}
async function update(){
var t=input.value;
if(!t){results.innerHTML='<span style="color:#71717a;">Enter text above</span>';return;}
var algos=[['SHA-1','SHA-1'],['SHA-256','SHA-256'],['SHA-384','SHA-384'],['SHA-512','SHA-512']];
var html='';
for(var i=0;i<algos.length;i++){
var name=algos[i][0],algo=algos[i][1];
var h=await hashText(algo,t);
html+='<div style="padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.04);cursor:pointer;" onclick="navigator.clipboard.writeText(this.dataset.h);this.style.background=\'rgba(74,222,128,0.1)\';var s=this;setTimeout(function(){s.style.background=\'\';},500)" data-h="'+h+'">';
html+='<span style="color:#a855f7;font-weight:600;font-size:10px;">'+name+'</span>';
html+='<div style="color:#a1a1aa;font-family:monospace;font-size:9px;word-break:break-all;">'+h+'</div></div>';
}
results.innerHTML=html;}
input.addEventListener('input',update);update();
