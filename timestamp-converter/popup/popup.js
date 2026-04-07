
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'timestamp_converter';
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
  const input = document.getElementById('input');
  const output = document.getElementById('output');
  const nowBtn = document.getElementById('now');
  
  function convert() {
    const val = input.value.trim();
    if (/^\d{10,13}$/.test(val)) {
      const ms = val.length === 10 ? val * 1000 : Number(val);
      const d = new Date(ms);
      output.textContent = d.toISOString() + '\n' + d.toLocaleString();
    } else {
      const d = new Date(val);
      if (!isNaN(d)) output.textContent = Math.floor(d.getTime()/1000) + '\n' + d.getTime();
      else output.textContent = 'Enter a timestamp or date';
    }
  }
  
  input.addEventListener('input', convert);
  nowBtn.addEventListener('click', () => {
    const now = Date.now();
    input.value = now;
    output.textContent = Math.floor(now/1000) + ' (seconds)\n' + now + ' (ms)\n' + new Date(now).toISOString();
  });
  nowBtn.click();
});