// LinkedIn Feed Hider — removes the feed column and recruiter spam banners
(function() {
  'use strict';
  const KEY = 'linkedin_hide_enabled';
  const SELECTORS = [
    '.feed-following-feed',          // main feed
    '.scaffold-layout__aside',       // right-side promoted posts
    '[data-control-name="sidebar_premium_cta"]', // premium upsell
    '.msg-overlay-bubble-header',    // messaging popups
    '.recruiter-banner',
    '.premium-upsell-link',
  ];

  function hide() {
    SELECTORS.forEach(sel => {
      document.querySelectorAll(sel).forEach(el => {
        el.style.setProperty('display', 'none', 'important');
      });
    });
  }

  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    hide();
    const obs = new MutationObserver(hide);
    obs.observe(document.body, { childList: true, subtree: true });
  });

  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE' && msg.enabled) hide();
  });
})();
