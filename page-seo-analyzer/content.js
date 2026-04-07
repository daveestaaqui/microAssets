// Page SEO Analyzer — collects meta data and sends to popup on request
(function() {
  'use strict';
  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type === 'SEO_ANALYZE') {
      const g = (sel) => {
        const el = document.querySelector(sel);
        return el ? (el.content || el.getAttribute('content') || el.textContent || '').trim() : '';
      };
      const h = (level) => Array.from(document.querySelectorAll(level)).map(e => e.textContent.trim());
      sendResponse({
        title: document.title,
        titleLen: document.title.length,
        desc: g('meta[name="description"]'),
        descLen: g('meta[name="description"]').length,
        canonical: g('link[rel="canonical"]') || location.href,
        ogTitle: g('meta[property="og:title"]'),
        ogDesc: g('meta[property="og:description"]'),
        ogImage: g('meta[property="og:image"]'),
        h1: h('h1'),
        h2Count: document.querySelectorAll('h2').length,
        imgsMissingAlt: document.querySelectorAll('img:not([alt])').length,
        wordCount: (document.body.innerText || '').split(/\s+/).filter(Boolean).length,
      });
    }
  });
})();
