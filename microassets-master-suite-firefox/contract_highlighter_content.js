// Contract Clause Highlighter
(function() {
  'use strict';
  const KEY = 'suite_license';

  const RISKY_PATTERNS = [
    { label: 'Indemnification', pattern: /indemnif(y|ication|ies)/gi, color: '#ffe066', risk: 'high' },
    { label: 'Auto-Renewal',    pattern: /auto-?renew/gi,               color: '#ff9933', risk: 'high' },
    { label: 'Arbitration',     pattern: /arbitrat(ion|or)/gi,          color: '#ff9933', risk: 'high' },
    { label: 'Non-Compete',     pattern: /non-?compete/gi,              color: '#ff4444', risk: 'critical' },
    { label: 'Liquidated Damages', pattern: /liquidated damages/gi,     color: '#ff4444', risk: 'critical' },
    { label: 'Limitation of Liability', pattern: /limitation of liability/gi, color: '#ffe066', risk: 'high' },
    { label: 'Governing Law',   pattern: /governing law|jurisdiction/gi, color: '#aaddff', risk: 'info' },
    { label: 'Confidentiality', pattern: /confidentialit(y|ies)/gi,     color: '#e0bbff', risk: 'medium' },
  ];

  function highlightText(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      let html = node.textContent;
      let replaced = false;
      RISKY_PATTERNS.forEach(({ pattern, color, label, risk }) => {
        pattern.lastIndex = 0;
        if (pattern.test(html)) {
          pattern.lastIndex = 0;
          html = html.replace(pattern, m =>
            `<mark style="background:${color};color:#000;border-radius:2px;padding:0 2px;cursor:help;" title="${label} (${risk})">${m}</mark>`
          );
          replaced = true;
        }
      });
      if (replaced) {
        const span = document.createElement('span');
        span.innerHTML = html;
        node.parentNode.replaceChild(span, node);
      }
    } else if (node.nodeType === Node.ELEMENT_NODE &&
               !['SCRIPT','STYLE','MARK'].includes(node.tagName)) {
      Array.from(node.childNodes).forEach(highlightText);
    }
  }

  chrome.storage.local.get(['suite_license', 'suite_enabled'], r => {
    if (r['suite_enabled'] === false || !r['suite_license']) return;
    highlightText(document.body);
  });

  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE' && msg.enabled) highlightText(document.body);
  });
})();
