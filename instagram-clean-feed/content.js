// Instagram Web Clean Feed
(function() {
  'use strict';
  const KEY = 'instagram_clean_enabled';
  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    const style = document.createElement('style');
    style.textContent = `
      /* Hide Suggested Posts section */
      article:has([data-testid="suggested-posts"]) { display: none !important; }
      /* Hide Reels */
      div[style*="reels"], a[href*="/reels/"] { display: none !important; }
      /* Hide Sponsored labels */
      article:has(span:is([class*="sponsored"], :contains("Sponsored"))) { opacity: 0.2; }
      /* Hide Explore/suggestions sidebar */
      aside[class*="suggest"], div[data-testid="suggested-user"] { display: none !important; }
    `;
    document.head.appendChild(style);
    // MutationObserver to catch dynamically loaded sponsored posts
    const obs = new MutationObserver(() => {
      document.querySelectorAll('article').forEach(article => {
        const text = article.textContent || '';
        if (text.includes('Sponsored') || text.includes('Suggested for you')) {
          article.style.display = 'none';
        }
      });
    });
    obs.observe(document.body || document.documentElement, { childList: true, subtree: true });
  });
  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE') location.reload();
  });
})();
