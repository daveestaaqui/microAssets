
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'diff_checker';
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
  const left = document.getElementById('left');
  const right = document.getElementById('right');
  const output = document.getElementById('output');
  
  document.getElementById('compare').onclick = () => {
    const lLines = left.value.split('\n');
    const rLines = right.value.split('\n');
    const maxLen = Math.max(lLines.length, rLines.length);
    let html = '';
    let added = 0, removed = 0, changed = 0;
    
    for (let i = 0; i < maxLen; i++) {
      const l = lLines[i] || '';
      const r = rLines[i] || '';
      if (l === r) {
        html += '<div style="font-size:11px;color:#888;padding:1px 4px;">' + (i+1) + ': ' + l.replace(/</g,'&lt;') + '</div>';
      } else if (!l) {
        html += '<div style="font-size:11px;color:#a6e3a1;background:rgba(166,227,161,0.1);padding:1px 4px;">+ ' + r.replace(/</g,'&lt;') + '</div>';
        added++;
      } else if (!r) {
        html += '<div style="font-size:11px;color:#f38ba8;background:rgba(243,139,168,0.1);padding:1px 4px;">- ' + l.replace(/</g,'&lt;') + '</div>';
        removed++;
      } else {
        html += '<div style="font-size:11px;color:#f9e2af;background:rgba(249,226,175,0.1);padding:1px 4px;">~ ' + l.replace(/</g,'&lt;') + ' → ' + r.replace(/</g,'&lt;') + '</div>';
        changed++;
      }
    }
    html = '<div style="margin-bottom:6px;font-size:11px;"><span style="color:#a6e3a1">+' + added + '</span> <span style="color:#f38ba8">-' + removed + '</span> <span style="color:#f9e2af">~' + changed + '</span></div>' + html;
    output.innerHTML = html;
  };
});