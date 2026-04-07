
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'hash_generator';
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
  
  async function hash(algo, data) {
    const encoder = new TextEncoder();
    const buf = await crypto.subtle.digest(algo, encoder.encode(data));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join('');
  }
  
  async function generateAll() {
    const text = input.value;
    if (!text) { output.innerHTML = '<div style="color:#888">Enter text to hash</div>'; return; }
    const sha256 = await hash('SHA-256', text);
    const sha1 = await hash('SHA-1', text);
    const sha512 = await hash('SHA-512', text);
    output.innerHTML = `<div style="margin-bottom:6px"><b style="color:#667eea">SHA-256:</b><br><span class="hash" style="font-size:11px;word-break:break-all;cursor:pointer" title="Click to copy">${sha256}</span></div><div style="margin-bottom:6px"><b style="color:#764ba2">SHA-1:</b><br><span class="hash" style="font-size:11px;word-break:break-all;cursor:pointer" title="Click to copy">${sha1}</span></div><div><b style="color:#f38ba8">SHA-512:</b><br><span class="hash" style="font-size:11px;word-break:break-all;cursor:pointer" title="Click to copy">${sha512}</span></div>`;
    output.querySelectorAll('.hash').forEach(el => el.onclick = () => { navigator.clipboard.writeText(el.textContent); el.style.color = '#a6e3a1'; setTimeout(() => el.style.color = '', 500); });
  }
  input.addEventListener('input', generateAll);
});