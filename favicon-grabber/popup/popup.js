
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'favicon_grabber';
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
    if (!tabs[0]) return;
    const url = new URL(tabs[0].url);
    const output = document.getElementById('output');
    const sizes = [16, 32, 64, 128, 256];
    const googleApi = 'https://www.google.com/s2/favicons?domain=' + url.hostname;
    
    output.innerHTML = '<div style="text-align:center;margin-bottom:12px"><img src="' + tabs[0].favIconUrl + '" width="64" style="border-radius:8px;background:#fff;padding:4px;"></div>';
    output.innerHTML += '<div style="color:#888;font-size:11px;margin-bottom:8px;">' + url.hostname + '</div>';
    output.innerHTML += '<div style="display:flex;flex-wrap:wrap;gap:6px;">';
    sizes.forEach(s => {
      output.innerHTML += '<div style="text-align:center;cursor:pointer" title="Click to copy URL"><img src="' + googleApi + '&sz=' + s + '" width="' + Math.min(s,48) + '" style="background:#fff;border-radius:4px;padding:2px;"><div style="color:#667eea;font-size:10px">' + s + 'px</div></div>';
    });
    output.innerHTML += '</div>';
    
    document.getElementById('copyUrl').onclick = () => navigator.clipboard.writeText(tabs[0].favIconUrl || googleApi + '&sz=64');
  });
});