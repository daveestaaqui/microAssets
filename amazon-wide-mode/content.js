// Amazon Wide Mode — expands the layout to full-width
(function() {
  'use strict';
  const KEY = 'amazon_wide_enabled';

  function expandLayout() {
    const style = document.createElement('style');
    style.id = '__sdal_amazon_wide__';
    style.textContent = `
      #a-page, .a-container, #dp, #desktop { max-width: 100% !important; width: 100% !important; }
      #ppd { max-width: 100% !important; }
      /* Highlight highly-rated products */
      [data-asin] .a-icon-star-small:first-child ~ .a-size-small { font-weight: bold; color: #f90 !important; }
    `;
    document.head.appendChild(style);
  }

  chrome.storage.local.get([KEY], r => {
    if (r[KEY] !== false) expandLayout();
  });

  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE') {
      if (msg.enabled) expandLayout();
      else { const s = document.getElementById('__sdal_amazon_wide__'); if (s) s.remove(); }
    }
  });
})();
