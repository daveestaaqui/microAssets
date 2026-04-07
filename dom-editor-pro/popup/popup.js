
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'live_dom_editor_pro';
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

document.getElementById('editBtn').onclick=()=>{chrome.tabs.query({active:true,currentWindow:true},tabs=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:()=>{document.body.contentEditable=document.body.contentEditable==='true'?'false':'true';if(document.body.contentEditable==='true'){document.body.style.outline='2px dashed rgba(168,85,247,0.5)';document.body.style.outlineOffset='-2px';}else{document.body.style.outline='none';}}});});};
let _domUses=0;
document.getElementById('hideBtn').onclick=()=>{_domUses++;chrome.storage.local.get(['omnisuite_pro_key_dom-editor-pro'],d=>{if(_domUses>3&&!d['omnisuite_pro_key_dom-editor-pro']){const g=document.getElementById('gate');if(g)g.style.display='block';return;}chrome.tabs.query({active:true,currentWindow:true},tabs=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:()=>{if(window._domHideMode){document.removeEventListener('click',window._domHideHandler,true);document.body.style.cursor='';window._domHideMode=false;return;}window._domHideMode=true;document.body.style.cursor='crosshair';window._domHideHandler=e=>{e.preventDefault();e.stopPropagation();e.target.style.display='none';};document.addEventListener('click',window._domHideHandler,true);}});});});};
document.getElementById('resetBtn').onclick=()=>{chrome.tabs.query({active:true,currentWindow:true},tabs=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:()=>location.reload()});});};
