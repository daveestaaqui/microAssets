// AI Content Bouncer — heuristic AI text detection
(function() {
  'use strict';
  const KEY = 'ai_bouncer_enabled';
  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    const AI_MARKERS = [
      /\bin conclusion\b/gi, /\bfurthermore\b/gi, /\bmoreover\b/gi,
      /\bdelve\b/gi, /\bit\s+is\s+worth\s+noting\b/gi,
      /\bfostere?\b/gi, /\btapestry\b/gi, /\blandscape\b/gi,
      /\bunleash\b/gi, /\beverchanging\b/gi, /\bparadigm\b/gi,
      /\bholistic\b/gi, /\bseamless\b/gi, /\bsynergy\b/gi,
    ];
    function scan() {
      document.querySelectorAll('p, li, span, div').forEach(el => {
        if (el.children.length > 3 || el.dataset.aiBounced) return;
        const text = el.textContent || '';
        if (text.length < 50) return;
        let score = 0;
        for (const re of AI_MARKERS) {
          if (re.test(text)) score++;
          re.lastIndex = 0;
        }
        if (score >= 3) {
          el.style.borderLeft = '3px solid #f59e0b';
          el.style.paddingLeft = '8px';
          el.title = 'AI Content Bouncer: Possible AI-generated text (' + score + ' markers)';
          el.dataset.aiBounced = '1';
        }
      });
    }
    setTimeout(scan, 2000);
  });
  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE' && msg.enabled) location.reload();
  });
})();
