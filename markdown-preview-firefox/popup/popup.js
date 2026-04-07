
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'markdown_preview';
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

const md=document.getElementById('md'),preview=document.getElementById('preview');
function render(){let t=md.value;t=t.replace(/^### (.*$)/gm,'<h3 style="font-size:14px;font-weight:bold;margin:8px 0 4px;">$1</h3>').replace(/^## (.*$)/gm,'<h2 style="font-size:16px;font-weight:bold;margin:10px 0 4px;">$1</h2>').replace(/^# (.*$)/gm,'<h1 style="font-size:18px;font-weight:bold;margin:12px 0 4px;">$1</h1>').replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\*(.*?)\*/g,'<em>$1</em>').replace(/`(.*?)`/g,'<code style="background:#e5e7eb;padding:1px 4px;border-radius:3px;font-size:11px;">$1</code>').replace(/^- (.*$)/gm,'<li style="margin-left:16px;">$1</li>').replace(/^\d+\. (.*$)/gm,'<li style="margin-left:16px;list-style:decimal;">$1</li>').replace(/\[(.*?)\]\((.*?)\)/g,'<a href="$2" style="color:#2563eb;">$1</a>').replace(/\n\n/g,'<br><br>').replace(/\n/g,'<br>');preview.innerHTML=t||'<span style="color:#9ca3af;">Preview will appear here…</span>';}
md.addEventListener('input',render);render();
