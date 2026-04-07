// LLM Privacy Scrub — intercepts paste events and redacts PII
(function() {
  'use strict';
  const KEY = 'llm_scrub_enabled';

  const PATTERNS = [
    { label: 'Email',   re: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,   mask: '[EMAIL]' },
    { label: 'Phone',   re: /\b(\+?1[-.]?)?(\(\d{3}\)|\d{3})[-.]?\d{3}[-.]?\d{4}\b/g, mask: '[PHONE]' },
    { label: 'SSN',     re: /\b\d{3}-\d{2}-\d{4}\b/g,                             mask: '[SSN]' },
    { label: 'CC',      re: /\b(?:\d[ -]?){13,16}\b/g,                              mask: '[CARD]' },
    { label: 'IP',      re: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g,                       mask: '[IP]' },
  ];

  function scrub(text) {
    let out = text;
    PATTERNS.forEach(({ re, mask }) => { out = out.replace(re, mask); });
    return out;
  }

  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    document.addEventListener('paste', (e) => {
      const raw = (e.clipboardData || window.clipboardData).getData('text');
      const clean = scrub(raw);
      if (clean !== raw) {
        e.preventDefault();
        const el = e.target;
        const start = el.selectionStart ?? 0;
        const end   = el.selectionEnd   ?? 0;
        // Insert cleaned text
        el.value = el.value.slice(0, start) + clean + el.value.slice(end);
        el.selectionStart = el.selectionEnd = start + clean.length;
        el.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }, true);
  });
})();
