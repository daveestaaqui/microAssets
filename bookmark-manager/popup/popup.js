
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'bookmark_manager_and_quick_search';
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

const search = document.getElementById('search');
const results = document.getElementById('results');

function renderBookmarks(bookmarks, query = '') {
  results.textContent = '';
  const flat = [];
  function flatten(nodes) {
    for (const n of nodes) {
      if (n.url) flat.push(n);
      if (n.children) flatten(n.children);
    }
  }
  flatten(bookmarks);
  
  const filtered = query 
    ? flat.filter(b => b.title.toLowerCase().includes(query) || b.url.toLowerCase().includes(query))
    : flat.slice(0, 50);
  
  if (filtered.length === 0) {
    results.innerHTML = '<p style="color:#71717a;text-align:center;padding:20px;">No bookmarks found</p>';
    return;
  }
  
  filtered.slice(0, 50).forEach(b => {
    const el = document.createElement('a');
    el.href = b.url;
    el.target = '_blank';
    el.style.cssText = 'display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:6px;text-decoration:none;color:#fafafa;transition:background 0.15s;';
    el.onmouseenter = () => el.style.background = 'rgba(255,255,255,0.08)';
    el.onmouseleave = () => el.style.background = 'transparent';
    
    const favicon = document.createElement('img');
    favicon.src = `https://www.google.com/s2/favicons?domain=${new URL(b.url).hostname}&sz=16`;
    favicon.width = 16; favicon.height = 16;
    favicon.style.cssText = 'border-radius:2px;flex-shrink:0;';
    
    const text = document.createElement('span');
    text.textContent = b.title || b.url;
    text.style.cssText = 'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
    
    el.appendChild(favicon);
    el.appendChild(text);
    results.appendChild(el);
  });
}

chrome.bookmarks.getTree(tree => renderBookmarks(tree));

search.addEventListener('input', () => {
  const q = search.value.toLowerCase().trim();
  chrome.bookmarks.getTree(tree => renderBookmarks(tree, q));
});

search.focus();
