// Tab Suspender content script — marks tab as active on user interaction
(function() {
  'use strict';
  const KEY = 'tab_suspender_enabled';
  // Signal to background that this tab has user activity
  ['mousemove','keydown','scroll','click'].forEach(evt => {
    document.addEventListener(evt, () => {
      chrome.runtime.sendMessage({ type: 'TAB_ACTIVE' }).catch(() => {});
    }, { once: true, passive: true });
  });
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'SUSPEND') {
      document.title = '💤 ' + document.title;
    }
  });
})();
