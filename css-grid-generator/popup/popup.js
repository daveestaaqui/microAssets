
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'css_grid_generator';
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
  const preview = document.getElementById('preview');
  const code = document.getElementById('code');
  const cols = document.getElementById('cols');
  const rows = document.getElementById('rows');
  const gap = document.getElementById('gap');
  
  function update() {
    const c = cols.value, r = rows.value, g = gap.value;
    preview.style.gridTemplateColumns = 'repeat('+c+', 1fr)';
    preview.style.gridTemplateRows = 'repeat('+r+', 1fr)';
    preview.style.gap = g+'px';
    preview.textContent = '';
    for (let i = 0; i < c*r; i++) {
      const cell = document.createElement('div');
      cell.style.cssText = 'background:rgba(102,126,234,0.3);border:1px solid rgba(102,126,234,0.5);border-radius:4px;min-height:20px;display:flex;align-items:center;justify-content:center;font-size:10px;color:#667eea;';
      cell.textContent = i+1;
      preview.appendChild(cell);
    }
    code.textContent = 'display: grid;\ngrid-template-columns: repeat('+c+', 1fr);\ngrid-template-rows: repeat('+r+', 1fr);\ngap: '+g+'px;';
  }
  
  [cols,rows,gap].forEach(el => el.addEventListener('input', update));
  document.getElementById('copy').onclick = () => navigator.clipboard.writeText(code.textContent);
  update();
});