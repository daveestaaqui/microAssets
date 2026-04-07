
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'json_path_finder';
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

const input=document.getElementById('input'),tree=document.getElementById('tree'),pathEl=document.getElementById('path');
function renderTree(obj,path='$',depth=0){let html='';const indent='  '.repeat(depth);if(typeof obj==='object'&&obj!==null){const isArr=Array.isArray(obj);const entries=isArr?obj.map((v,i)=>[i,v]):Object.entries(obj);entries.forEach(([k,v])=>{const p=isArr?`${path}[${k}]`:`${path}.${k}`;const isObj=typeof v==='object'&&v!==null;html+=`<div style="padding:1px 0;cursor:pointer;" onmouseover="this.style.background='rgba(168,85,247,0.1)'" onmouseout="this.style.background=''" onclick="event.stopPropagation();setPath('${p}')">${indent}<span style="color:#7dd3fc;">${isArr?k:'"'+k+'"'}</span>: ${isObj?'{…}':'<span style="color:#fde68a;">'+JSON.stringify(v)+'</span>'}</div>`;if(isObj)html+=renderTree(v,p,depth+1);});}return html;}
window.setPath=p=>{pathEl.textContent=p;navigator.clipboard.writeText(p);pathEl.style.borderColor='rgba(74,222,128,0.5)';setTimeout(()=>pathEl.style.borderColor='',1000);};
pathEl.onclick=()=>navigator.clipboard.writeText(pathEl.textContent);
input.addEventListener('input',()=>{try{const obj=JSON.parse(input.value);tree.innerHTML=renderTree(obj);pathEl.textContent='Click any value to get its path';}catch(e){tree.innerHTML='<span style="color:#f87171;">Invalid JSON</span>';pathEl.textContent='';}});
