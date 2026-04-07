// Auto Cookie-Banner Rejector
(function() {
  'use strict';
  const ENABLED_KEY = 'cookie_banner_enabled';
  chrome.storage.local.get([ENABLED_KEY], r => {
    if (r[ENABLED_KEY] === false) return;
    // Common cookie banner selectors
    const selectors = [
      '[class*="cookie-banner"]', '[class*="cookie-consent"]', '[class*="cookie-notice"]',
      '[id*="cookie-banner"]', '[id*="cookie-consent"]', '[id*="cookie-notice"]',
      '[class*="gdpr"]', '[id*="gdpr"]', '[class*="cc-banner"]',
      '[class*="consent-banner"]', '[id*="consent-banner"]',
      '[class*="CookieConsent"]', '[id*="CookieConsent"]',
      '.cookie-bar', '#cookie-bar', '.cookie-popup', '#cookie-popup',
      '[aria-label*="cookie" i]', '[aria-label*="consent" i]',
      '[class*="onetrust"]', '#onetrust-banner-sdk',
      '.cc-window', '.cc-banner',
    ];
    const acceptBtnSelectors = [
      'button[class*="accept" i]', 'button[class*="agree" i]', 'button[class*="allow" i]',
      'button[class*="consent" i]', 'a[class*="accept" i]', 'a[class*="agree" i]',
      '[id*="accept" i]', '[id*="agree" i]',
      'button[aria-label*="accept" i]', 'button[aria-label*="agree" i]',
      '.cc-accept', '.cc-allow', '.cc-dismiss',
    ];
    function tryDismiss() {
      // Try clicking accept/agree buttons first
      for (const sel of acceptBtnSelectors) {
        const btn = document.querySelector(sel);
        if (btn && btn.offsetParent !== null) { btn.click(); return true; }
      }
      // Try hiding banners directly
      for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el && el.offsetParent !== null) { el.style.display = 'none'; return true; }
      }
      return false;
    }
    // Retry several times as banners load asynchronously
    tryDismiss();
    setTimeout(tryDismiss, 1000);
    setTimeout(tryDismiss, 2500);
    setTimeout(tryDismiss, 5000);
    const obs = new MutationObserver(() => { tryDismiss(); });
    obs.observe(document.documentElement, { childList: true, subtree: true });
    setTimeout(() => obs.disconnect(), 15000);
  });
})();
