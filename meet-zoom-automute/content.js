// Content Script — Google Meet Auto-Muter
// v1.2.1 — Robust multi-strategy selectors & full SPA navigation support

(function() {
  'use strict';

  if (/^(chrome|chrome-extension|moz-extension|about):/.test(window.location.protocol)) return;

  const STORAGE_KEY = 'meet_zoom_automute_enabled';
  let micDone = false;
  let camDone = false;
  let isEnabled = true;

  function robustClick(el) {
    if (!el || el.offsetParent === null) return false;
    // Dispatch mouse events to wake up React handlers
    el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
    el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
    el.click();
    return true;
  }

  function findAndClick(type) {
    const isMic = type === 'mic';
    
    // Google Meet's generic attributes
    const labels = isMic ? ['Turn off microphone', 'Mute microphone', 'Microphone', 'Mikrofon', 'micro'] : ['Turn off camera', 'Turn off video', 'Camera', 'Video', 'Kamera', 'caméra'];
    
    // 1. Check data-is-muted specifically (highest confidence)
    const exactMuteButtons = document.querySelectorAll('[data-is-muted="false"], [data-is-muted="false"] *');
    for (const b of exactMuteButtons) {
      const parent = b.closest('button, [role="button"]');
      if (!parent) continue;
      const t = (parent.getAttribute('aria-label') || parent.getAttribute('data-tooltip') || '').toLowerCase();
      if (isMic && (t.includes('mic') || t.includes('micro'))) {
         return robustClick(parent);
      }
      if (!isMic && (t.includes('cam') || t.includes('video'))) {
         return robustClick(parent);
      }
    }

    // 2. Fallback to robust label scanning
    const buttons = document.querySelectorAll('button, [role="button"]');
    for (const btn of buttons) {
      const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
      const tool = (btn.getAttribute('data-tooltip') || '').toLowerCase();
      const combined = aria + ' ' + tool;

      for (const label of labels) {
        if (combined.includes(label.toLowerCase())) {
          // ensure it's not the "Turn ON" button which implies it's already muted
          if (!combined.includes('turn on') && !combined.includes('unmute')) {
             return robustClick(btn);
          }
        }
      }
    }
    return false;
  }

  function attemptMute() {
    if (!isEnabled) return;
    
    // Only attempt on actual meeting pages, not the home screen (which is just meet.google.com/)
    if (window.location.pathname.length < 5) return;

    if (!micDone) micDone = findAndClick('mic');
    if (!camDone) camDone = findAndClick('cam');
  }

  // --- SPA Navigation & Mutation Observer logic ---
  let lastUrl = location.href;
  
  const observer = new MutationObserver(() => {
    // Check if URL changed (SPA navigation)
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      // Reset state on new page
      micDone = false;
      camDone = false;
    }
    attemptMute();
  });

  chrome.storage.local.get([STORAGE_KEY], (result) => {
    if (result[STORAGE_KEY] === false) isEnabled = false;
    
    if (isEnabled) {
      observer.observe(document.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['aria-label', 'data-tooltip', 'data-is-muted']
      });
      
      // Kickstart
      setInterval(attemptMute, 1000);
    }
  });

  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'TOGGLE') {
      isEnabled = msg.enabled;
      if (isEnabled) attemptMute();
    }
  });

})();
