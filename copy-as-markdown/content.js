// Copy as Markdown — listens for copy-link command from popup
(function() {
  'use strict';
  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type === 'COPY_MD') {
      const sel = window.getSelection().toString().trim();
      const md = sel
        ? `[${sel}](${location.href})`
        : `[${document.title}](${location.href})`;
      navigator.clipboard.writeText(md).then(() => {
        sendResponse({ ok: true });
      }).catch(() => {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = md;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
        sendResponse({ ok: true });
      });
      return true; // keep channel open
    }
  });
})();
