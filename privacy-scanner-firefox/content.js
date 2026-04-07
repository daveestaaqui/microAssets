// Privacy Scanner — detects third-party trackers and analytics
(function() {
  'use strict';

  const KNOWN_TRACKERS = [
    'google-analytics.com', 'googletagmanager.com', 'doubleclick.net',
    'facebook.net', 'connect.facebook.net', 'analytics.twitter.com',
    'static.ads-twitter.com', 'snap.licdn.com', 'platform.linkedin.com',
    'hotjar.com', 'mouseflow.com', 'fullstory.com', 'segment.io',
    'segment.com', 'mixpanel.com', 'amplitude.com', 'heap.io',
    'crazyegg.com', 'inspectlet.com', 'pingdom.net',
  ];

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type !== 'PRIVACY_SCAN') return;

    const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
    const iframes = Array.from(document.querySelectorAll('iframe[src]')).map(i => i.src);
    const images  = Array.from(document.querySelectorAll('img[src]')).map(i => i.src);
    const allUrls = [...scripts, ...iframes, ...images];

    const trackers = [];
    KNOWN_TRACKERS.forEach(tracker => {
      const found = allUrls.filter(u => u.includes(tracker));
      if (found.length) trackers.push({ tracker, count: found.length });
    });

    const hasConsent = !!(
      document.querySelector('[class*="cookie"]') ||
      document.querySelector('[class*="consent"]') ||
      document.querySelector('[id*="cookie"]') ||
      document.querySelector('[id*="gdpr"]')
    );

    const score = Math.max(0, 100 - (trackers.length * 12) - (hasConsent ? 0 : 20));
    sendResponse({ trackers, hasConsent, score, url: location.href });
  });
})();
