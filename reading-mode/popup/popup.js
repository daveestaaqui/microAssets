
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'reader_mode__clean_articles';
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

const sizeSlider=document.getElementById('fontSize'),sizeVal=document.getElementById('sizeVal');
sizeSlider.oninput=()=>sizeVal.textContent=sizeSlider.value;
document.getElementById('activateBtn').onclick=()=>{const theme=document.querySelector('input[name=theme]:checked').value;const size=sizeSlider.value;
chrome.tabs.query({active:true,currentWindow:true},(tabs)=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},args:[theme,size],func:(theme,size)=>{
const article=document.querySelector('article')||document.querySelector('[role=main]')||document.querySelector('main')||document.body;const content=article.innerHTML;
const bg=theme==='dark'?'#1a1a2e':theme==='sepia'?'#f4ecd8':'#ffffff';const fg=theme==='dark'?'#e0e0e0':theme==='sepia'?'#5b4636':'#333333';
document.body.innerHTML='<div style="max-width:680px;margin:40px auto;padding:20px 40px;font-family:Georgia,serif;font-size:'+size+'px;line-height:1.8;color:'+fg+';background:'+bg+';min-height:100vh;">'+content+'</div>';document.body.style.background=bg;document.body.style.margin='0';
}});});};
