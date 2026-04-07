// Time Tracker — reports active tab time to background service worker
(function() {
  'use strict';
  let active = true;
  let lastPing = Date.now();

  // Visibility
  document.addEventListener('visibilitychange', () => {
    active = !document.hidden;
    chrome.runtime.sendMessage({ type: 'VISIBILITY', active, url: location.href }).catch(() => {});
  });

  // Idle detection
  ['mousemove','keydown','scroll','click'].forEach(evt => {
    document.addEventListener(evt, () => {
      if (!active) return;
      const now = Date.now();
      if (now - lastPing > 30000) { // report at most every 30s
        lastPing = now;
        chrome.runtime.sendMessage({ type: 'PING', url: location.href }).catch(() => {});
      }
    }, { passive: true });
  });

  // Initial ping
  chrome.runtime.sendMessage({ type: 'START', url: location.href, title: document.title }).catch(() => {});
})();
