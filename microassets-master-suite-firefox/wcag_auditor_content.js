// WCAG Auditor — full accessibility audit content script
(function() {
  'use strict';
  const ENABLED_KEY = 'suite_enabled';
  const LICENSE_KEY = 'suite_license';

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type !== 'RUN_AUDIT') return;

    const issues = [];

    // 1. Images without alt text
    document.querySelectorAll('img').forEach(img => {
      if (!img.hasAttribute('alt')) {
        issues.push({ type: 'error', rule: '1.1.1', msg: `Image missing alt: ${img.src.split('/').pop()}` });
      }
    });

    // 2. Heading hierarchy
    const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6'));
    let prevLevel = 0;
    headings.forEach(h => {
      const level = parseInt(h.tagName[1]);
      if (prevLevel && level > prevLevel + 1) {
        issues.push({ type: 'warning', rule: '1.3.1', msg: `Skipped heading level: ${h.tagName} after H${prevLevel}` });
      }
      prevLevel = level;
    });

    // 3. Form labels
    document.querySelectorAll('input,select,textarea').forEach(input => {
      const id = input.id;
      if (id && !document.querySelector(`label[for="${id}"]`) && !input.getAttribute('aria-label')) {
        issues.push({ type: 'error', rule: '1.3.1', msg: `Form input #${id} missing label` });
      }
    });

    // 4. Links with no discernible text
    document.querySelectorAll('a').forEach(a => {
      const text = (a.textContent || '').trim();
      const ariaLabel = a.getAttribute('aria-label') || '';
      if (!text && !ariaLabel && !a.querySelector('img[alt]')) {
        issues.push({ type: 'error', rule: '2.4.4', msg: `Link with no text or aria-label: ${a.href}` });
      }
    });

    // 5. Color contrast (approximate check using inline styles)
    document.querySelectorAll('[style*="color"]').forEach(el => {
      const style = el.getAttribute('style') || '';
      const bg = getComputedStyle(el).backgroundColor;
      const fg = getComputedStyle(el).color;
      if (bg === fg) {
        issues.push({ type: 'error', rule: '1.4.3', msg: `Possible zero-contrast text element: ${el.tagName}` });
      }
    });

    sendResponse({ issues, url: location.href, checked: Date.now() });
  });

  chrome.storage.local.get([ENABLED_KEY, LICENSE_KEY], r => {
    if (r[ENABLED_KEY] === false || !r[LICENSE_KEY]) return;
    // Auto-highlight on load (lightweight pass)
    document.querySelectorAll('img:not([alt])').forEach(img => {
      img.style.outline = '2px solid red';
      img.title = 'WCAG: Missing alt text';
    });
  });
})();
