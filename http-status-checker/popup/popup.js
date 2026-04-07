
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'http_status_checker';
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


document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('url');
  const btn = document.getElementById('check');
  const output = document.getElementById('output');
  
  chrome.tabs.query({active: true, currentWindow: true}, tabs => {
    if (tabs[0]) input.value = tabs[0].url;
  });
  
  btn.onclick = async () => {
    const url = input.value.trim();
    if (!url) return;
    output.innerHTML = '<div style="color:#888;">Checking...</div>';
    try {
      const start = Date.now();
      const res = await fetch(url, {method: 'HEAD', mode: 'no-cors'});
      const time = Date.now() - start;
      const status = res.status || 0;
      const color = status < 300 ? '#a6e3a1' : status < 400 ? '#f9e2af' : '#f38ba8';
      output.innerHTML = '<div style="text-align:center;margin-bottom:8px;"><div style="font-size:36px;font-weight:bold;color:'+color+';">'+( status || 'CORS')+'</div><div style="color:#888;font-size:11px;">'+time+'ms response time</div></div>';
      output.innerHTML += '<div style="font-size:11px;color:#888;">Type: '+res.type+'</div>';
    } catch(e) {
      output.innerHTML = '<div style="color:#f38ba8;text-align:center;"><div style="font-size:36px;">❌</div><div>'+e.message+'</div></div>';
    }
  };
});