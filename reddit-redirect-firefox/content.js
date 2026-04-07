// Old Reddit Redirect — switches to old.reddit.com on the new redesign
(function() {
  'use strict';
  const KEY = 'reddit_redirect_enabled';

  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    // Detect new Reddit (sh.reddit.com or www.reddit.com with new design)
    if (location.hostname === 'www.reddit.com' ||
        location.hostname === 'sh.reddit.com') {
      const newUrl = location.href.replace(/^https?:\/\/(www|sh)\.reddit\.com/, 'https://old.reddit.com');
      if (location.href !== newUrl) {
        location.replace(newUrl);
        return;
      }
    }
    // On old Reddit: hide promoted posts
    document.querySelectorAll('.promoted').forEach(el => el.remove());
    const obs = new MutationObserver(() => {
      document.querySelectorAll('.promoted').forEach(el => el.remove());
    });
    obs.observe(document.body, { childList: true, subtree: true });
  });
})();
