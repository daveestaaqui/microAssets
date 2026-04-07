// GitHub Line Numbers — makes line numbers sticky and clickable links colorful
(function() {
  'use strict';
  const KEY = 'github_linenums_enabled';

  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    enhance();
  });

  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE') {
      if (msg.enabled) enhance();
    }
  });

  function enhance() {
    const style = document.createElement('style');
    style.textContent = `
      /* Sticky line numbers in file diffs */
      .blob-num { position: sticky !important; left: 0; background: #0d1117; z-index: 1; }
      /* Highlight hovered diff line */
      .diff-table tr:hover td { background: #ffffff08 !important; }
      /* Better contrast for additions/deletions */
      .blob-code-addition { background: #1a3a1a !important; }
      .blob-code-deletion { background: #3a1a1a !important; }
      /* Softer focus on selected line */
      .highlighted { background: #2a2a5a !important; }
    `;
    document.head.appendChild(style);
  }
})();
