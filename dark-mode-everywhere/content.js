// Dark Mode Everywhere — injects a dark CSS filter
(function() {
  'use strict';
  const KEY = 'dark_mode_enabled';
  const STYLE_ID = '__sdal_dark_mode__';

  function applyDark() {
    if (document.getElementById(STYLE_ID)) return;
    const s = document.createElement('style');
    s.id = STYLE_ID;
    s.textContent = `
      html { filter: invert(1) hue-rotate(180deg) !important; }
      img, video, canvas, svg, picture, [style*="background-image"] {
        filter: invert(1) hue-rotate(180deg) !important;
      }
    `;
    document.documentElement.appendChild(s);
  }

  function removeDark() {
    const s = document.getElementById(STYLE_ID);
    if (s) s.remove();
  }

  chrome.storage.local.get([KEY], r => {
    if (r[KEY] !== false) applyDark();
  });

  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE') {
      if (msg.enabled) applyDark(); else removeDark();
    }
  });
})();
