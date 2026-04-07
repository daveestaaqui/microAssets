// Google Docs Focus Mode — hides toolbars on demand
(function() {
  'use strict';
  const KEY = 'gdocs_focus_enabled';
  const SELECTORS = ['#docs-toolbar', '#docs-menudrawercontainer', '.docs-gm', '#kix-appview .kix-header'];

  function hide() {
    SELECTORS.forEach(sel => {
      document.querySelectorAll(sel).forEach(el => {
        el.style.setProperty('display', 'none', 'important');
      });
    });
    const editor = document.querySelector('#kix-appview .kix-page');
    if (editor) editor.style.marginTop = '20px';
  }

  function show() {
    SELECTORS.forEach(sel => {
      document.querySelectorAll(sel).forEach(el => el.style.removeProperty('display'));
    });
  }

  chrome.storage.local.get([KEY], r => {
    if (r[KEY] !== false) setTimeout(hide, 1500);
  });

  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE') { if (msg.enabled) hide(); else show(); }
  });
})();
