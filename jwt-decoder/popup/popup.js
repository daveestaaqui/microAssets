
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'jwt_decoder';
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
  
  function decodeJWT() {
    const token = input.value.trim();
    if (!token) { output.innerHTML = '<div style="color:#888">Paste a JWT token</div>'; return; }
    try {
      const parts = token.split('.');
      if (parts.length !== 3) throw new Error('Invalid JWT');
      const header = JSON.parse(atob(parts[0]));
      const payload = JSON.parse(atob(parts[1].replace(/-/g,'+').replace(/_/g,'/')));
      let expInfo = '';
      if (payload.exp) {
        const expDate = new Date(payload.exp * 1000);
        const isExpired = expDate < new Date();
        expInfo = '<div style="margin-top:6px;padding:6px;background:' + (isExpired ? 'rgba(243,139,168,0.15)' : 'rgba(166,227,161,0.15)') + ';border-radius:4px;color:' + (isExpired ? '#f38ba8' : '#a6e3a1') + '">' + (isExpired ? '⛔ Expired: ' : '✅ Expires: ') + expDate.toLocaleString() + '</div>';
      }
      output.innerHTML = '<div style="margin-bottom:8px"><b style="color:#667eea">Header:</b><pre style="font-size:11px;margin:4px 0;white-space:pre-wrap">' + JSON.stringify(header, null, 2) + '</pre></div><div><b style="color:#764ba2">Payload:</b><pre style="font-size:11px;margin:4px 0;white-space:pre-wrap">' + JSON.stringify(payload, null, 2) + '</pre></div>' + expInfo;
    } catch(e) { output.innerHTML = '<div style="color:#f38ba8">Invalid JWT: ' + e.message + '</div>'; }
  }
  input.addEventListener('input', decodeJWT);
});