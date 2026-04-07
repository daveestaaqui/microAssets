
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'carbon_footprint_checker';
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
  chrome.tabs.query({active: true, currentWindow: true}, tabs => {
    chrome.scripting.executeScript({target: {tabId: tabs[0].id}, func: () => {
      const entries = performance.getEntriesByType('resource');
      let totalBytes = 0;
      entries.forEach(e => totalBytes += e.transferSize || 0);
      const docSize = new Blob([document.documentElement.outerHTML]).size;
      totalBytes += docSize;
      const images = document.images.length;
      const scripts = document.scripts.length;
      return { bytes: totalBytes, images, scripts, url: location.hostname };
    }}, results => {
      const data = results[0].result;
      const kb = (data.bytes / 1024).toFixed(0);
      const mb = (data.bytes / 1024 / 1024).toFixed(2);
      const co2 = (data.bytes * 0.0000002).toFixed(4); // ~0.2g per MB
      const grade = kb < 500 ? 'A' : kb < 1000 ? 'B' : kb < 2000 ? 'C' : kb < 5000 ? 'D' : 'F';
      const color = {A:'#a6e3a1',B:'#a6e3a1',C:'#f9e2af',D:'#fab387',F:'#f38ba8'}[grade];
      
      document.getElementById('output').innerHTML = 
        '<div style="text-align:center;margin-bottom:12px;"><div style="font-size:48px;font-weight:bold;color:'+color+'">'+grade+'</div><div style="color:#888;font-size:12px;">'+data.url+'</div></div>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">' +
        '<div style="background:#1e1e2e;padding:8px;border-radius:6px;text-align:center;"><div style="color:#667eea;font-size:16px;font-weight:bold;">'+kb+'KB</div><div style="color:#888;font-size:10px;">Page Weight</div></div>' +
        '<div style="background:#1e1e2e;padding:8px;border-radius:6px;text-align:center;"><div style="color:#764ba2;font-size:16px;font-weight:bold;">'+co2+'g</div><div style="color:#888;font-size:10px;">CO₂ per visit</div></div>' +
        '<div style="background:#1e1e2e;padding:8px;border-radius:6px;text-align:center;"><div style="color:#f9e2af;font-size:16px;font-weight:bold;">'+data.images+'</div><div style="color:#888;font-size:10px;">Images</div></div>' +
        '<div style="background:#1e1e2e;padding:8px;border-radius:6px;text-align:center;"><div style="color:#f38ba8;font-size:16px;font-weight:bold;">'+data.scripts+'</div><div style="color:#888;font-size:10px;">Scripts</div></div></div>';
    });
  });
});