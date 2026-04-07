
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'github_quick_stats';
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
  const output = document.getElementById('output');
  
  chrome.tabs.query({active: true, currentWindow: true}, async tabs => {
    if (!tabs[0]) return;
    const url = new URL(tabs[0].url);
    
    if (url.hostname !== 'github.com') {
      output.innerHTML = '<div style="text-align:center;color:#888;"><div style="font-size:32px;">��</div><div>Open a GitHub repo to see stats</div></div>';
      return;
    }
    
    const parts = url.pathname.split('/').filter(Boolean);
    if (parts.length < 2) {
      output.innerHTML = '<div style="color:#888;">Navigate to a specific repo</div>';
      return;
    }
    
    const owner = parts[0], repo = parts[1];
    output.innerHTML = '<div style="color:#888;text-align:center;">Loading stats for ' + owner + '/' + repo + '...</div>';
    
    try {
      const res = await fetch('https://api.github.com/repos/' + owner + '/' + repo);
      const data = await res.json();
      
      if (data.message) {
        output.innerHTML = '<div style="color:#f38ba8;">' + data.message + '</div>';
        return;
      }
      
      output.innerHTML = '<div style="text-align:center;margin-bottom:12px;"><div style="color:#fff;font-weight:bold;font-size:14px;">' + data.full_name + '</div><div style="color:#888;font-size:11px;margin-top:2px;">' + (data.description || '').substring(0,80) + '</div></div>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">' +
        '<div style="background:#1e1e2e;padding:8px;border-radius:6px;text-align:center;"><div style="color:#f9e2af;font-size:18px;font-weight:bold;">⭐ ' + data.stargazers_count.toLocaleString() + '</div><div style="color:#888;font-size:10px;">Stars</div></div>' +
        '<div style="background:#1e1e2e;padding:8px;border-radius:6px;text-align:center;"><div style="color:#89b4fa;font-size:18px;font-weight:bold;">🍴 ' + data.forks_count.toLocaleString() + '</div><div style="color:#888;font-size:10px;">Forks</div></div>' +
        '<div style="background:#1e1e2e;padding:8px;border-radius:6px;text-align:center;"><div style="color:#a6e3a1;font-size:18px;font-weight:bold;">👁️ ' + data.watchers_count.toLocaleString() + '</div><div style="color:#888;font-size:10px;">Watchers</div></div>' +
        '<div style="background:#1e1e2e;padding:8px;border-radius:6px;text-align:center;"><div style="color:#f38ba8;font-size:18px;font-weight:bold;">🐛 ' + data.open_issues_count + '</div><div style="color:#888;font-size:10px;">Issues</div></div></div>' +
        '<div style="margin-top:8px;font-size:11px;color:#888;text-align:center;">📝 ' + (data.language || 'N/A') + ' | 📏 ' + (data.size/1024).toFixed(1) + 'MB | ' + (data.license ? '📄 ' + data.license.spdx_id : '❌ No license') + '</div>';
    } catch(e) {
      output.innerHTML = '<div style="color:#f38ba8;">Error: ' + e.message + '</div>';
    }
  });
});