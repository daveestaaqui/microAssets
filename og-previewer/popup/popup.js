
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'open_graph_previewer';
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
      const getMeta = (p) => {
        const el = document.querySelector('meta[property="'+p+'"]') || document.querySelector('meta[name="'+p+'"]');
        return el ? el.content : '';
      };
      return { title: getMeta('og:title') || document.title, desc: getMeta('og:description') || getMeta('description'), image: getMeta('og:image'), url: getMeta('og:url') || location.href, type: getMeta('og:type') || 'website' };
    }}, results => {
      const og = results[0].result;
      const output = document.getElementById('output');
      let html = '<div style="background:#1e1e2e;border-radius:8px;overflow:hidden;border:1px solid #45475a;">';
      if (og.image) html += '<img src="'+og.image+'" style="width:100%;height:100px;object-fit:cover;">';
      html += '<div style="padding:8px;"><div style="color:#667eea;font-size:10px;text-transform:uppercase;">'+og.type+'</div>';
      html += '<div style="color:#fff;font-weight:bold;font-size:13px;margin:4px 0;">'+og.title+'</div>';
      html += '<div style="color:#888;font-size:11px;">'+og.desc.substring(0,120)+'</div>';
      html += '<div style="color:#667eea;font-size:10px;margin-top:4px;">'+new URL(og.url).hostname+'</div>';
      html += '</div></div>';
      output.innerHTML = html;
    });
  });
});