

// === OmniSuite Pro Upsell (usage-gated) ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const PRO_KEY = 'ma_pro_dismissed';
  const PRO_BOUGHT_KEY = 'ma_pro_active';

  _api.storage.local.get([PRO_KEY, PRO_BOUGHT_KEY, 'tab_groups_saver_and_restorer_usage'], (r) => {
    if (r[PRO_BOUGHT_KEY] || r[PRO_KEY]) return;
    const usage = r['tab_groups_saver_and_restorer_usage'] || 0;
    if (usage >= 10) {
      const banner = document.getElementById('ma-pro-upsell');
      if (banner) banner.style.display = 'block';
    }
  });

  const dismissBtn = document.getElementById('ma-dismiss-pro');
  if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
      _api.storage.local.set({ [PRO_KEY]: true });
      const banner = document.getElementById('ma-pro-upsell');
      if (banner) banner.style.display = 'none';
    });
  }
})();

// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'tab_groups_saver_and_restorer';
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

const saveBtn = document.getElementById('saveBtn');
const groupName = document.getElementById('groupName');
const sessionsDiv = document.getElementById('sessions');

function render() {
  chrome.storage.local.get(['tabGroups'], (data) => {
    const groups = data.tabGroups || {};
    sessionsDiv.textContent = '';
    const names = Object.keys(groups).reverse();
    if (names.length === 0) {
      sessionsDiv.innerHTML = '<p style="color:#71717a;text-align:center;padding:20px;">No saved sessions yet</p>';
      return;
    }
    names.forEach(name => {
      const row = document.createElement('div');
      row.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:8px;border-radius:8px;margin-bottom:4px;background:rgba(255,255,255,0.03);';
      
      const info = document.createElement('div');
      info.innerHTML = `<strong style="color:#fafafa;">${name}</strong><br><span style="color:#71717a;font-size:11px;">${groups[name].length} tabs</span>`;
      
      const btns = document.createElement('div');
      btns.style.cssText = 'display:flex;gap:6px;';
      
      const restoreBtn = document.createElement('button');
      restoreBtn.textContent = '↗ Open';
      restoreBtn.style.cssText = 'padding:4px 10px;border-radius:6px;border:1px solid rgba(168,85,247,0.4);background:rgba(168,85,247,0.15);color:#c084fc;font-size:11px;cursor:pointer;';
      restoreBtn.onclick = () => { groups[name].forEach(url => chrome.tabs.create({ url, active: false })); };
      
      const delBtn = document.createElement('button');
      delBtn.textContent = '✕';
      delBtn.style.cssText = 'padding:4px 8px;border-radius:6px;border:1px solid rgba(239,68,68,0.3);background:rgba(239,68,68,0.1);color:#f87171;font-size:11px;cursor:pointer;';
      delBtn.onclick = () => { delete groups[name]; chrome.storage.local.set({ tabGroups: groups }, render); };
      
      btns.appendChild(restoreBtn);
      btns.appendChild(delBtn);
      row.appendChild(info);
      row.appendChild(btns);
      sessionsDiv.appendChild(row);
    });
  });
}

saveBtn.addEventListener('click', () => {
  const name = groupName.value.trim() || `Session ${new Date().toLocaleString()}`;
  chrome.tabs.query({ currentWindow: true }, (tabs) => {
    const urls = tabs.map(t => t.url).filter(u => u && !u.startsWith('chrome://'));
    chrome.storage.local.get(['tabGroups'], (data) => {
      const groups = data.tabGroups || {};
      groups[name] = urls;
      chrome.storage.local.set({ tabGroups: groups }, () => {
        groupName.value = '';
        render();
      });
    });
  });
});

render();
