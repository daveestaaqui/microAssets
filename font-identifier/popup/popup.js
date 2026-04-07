
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'font_identifier_and_css_inspector';
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

const inspectBtn = document.getElementById('inspectBtn');
const results = document.getElementById('results');

inspectBtn.addEventListener('click', () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      func: () => {
        // Remove any existing overlay
        if (document.getElementById('__flowkit_font_overlay')) {
          document.getElementById('__flowkit_font_overlay').remove();
          return null;
        }
        
        return new Promise((resolve) => {
          const overlay = document.createElement('div');
          overlay.id = '__flowkit_font_overlay';
          overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:999999;cursor:crosshair;';
          document.body.appendChild(overlay);
          
          overlay.addEventListener('click', (e) => {
            overlay.remove();
            const el = document.elementFromPoint(e.clientX, e.clientY);
            if (!el) { resolve(null); return; }
            const cs = window.getComputedStyle(el);
            resolve({
              fontFamily: cs.fontFamily,
              fontSize: cs.fontSize,
              fontWeight: cs.fontWeight,
              lineHeight: cs.lineHeight,
              color: cs.color,
              letterSpacing: cs.letterSpacing
            });
          });
        });
      }
    }, (injectionResults) => {
      if (injectionResults && injectionResults[0] && injectionResults[0].result) {
        const r = injectionResults[0].result;
        document.getElementById('fontFamily').textContent = r.fontFamily.split(',')[0].replace(/['"]/g, '');
        document.getElementById('fontSize').textContent = r.fontSize;
        document.getElementById('fontWeight').textContent = r.fontWeight;
        document.getElementById('lineHeight').textContent = r.lineHeight;
        document.getElementById('fontColor').textContent = r.color;
        document.getElementById('letterSpacing').textContent = r.letterSpacing;
        results.style.display = 'block';
      }
    });
  });
});
