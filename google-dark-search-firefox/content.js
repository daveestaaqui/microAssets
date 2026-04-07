// Google Dark Search
(function() {
  'use strict';
  const KEY = 'google_dark_enabled';
  function applyDark() {
    const style = document.createElement('style');
    style.id = 'google-dark-search-style';
    style.textContent = `
      html, body { background: #1a1a2e !important; color: #e0e0e0 !important; }
      #search, #main, #cnt, .g, .tF2Cxc { background: transparent !important; color: #ccc !important; }
      .LC20lb { color: #8ab4f8 !important; }
      .VwiC3b, .IsZvec { color: #bdc1c6 !important; }
      a:visited .LC20lb { color: #c58af9 !important; }
      #searchform, .sfbg, .RNNXgb { background: #2a2a3e !important; }
      input[name="q"] { background: #333 !important; color: #fff !important; }
      .MV3Tnb, .aajZCb { background: #2a2a3e !important; }
      .minidiv .sfbg { background: #1a1a2e !important; }
      #appbar, #hdtb, .ct68jc { background: #1e1e30 !important; border-color: #333 !important; }
      .hdtb-mitem a, .hdtb-mitem { color: #8ab4f8 !important; }
      img { opacity: 0.9; }
    `;
    document.head.appendChild(style);
  }
  function removeDark() {
    const s = document.getElementById('google-dark-search-style');
    if (s) s.remove();
  }
  chrome.storage.local.get([KEY], r => {
    if (r[KEY] !== false) applyDark();
  });
  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE') msg.enabled ? applyDark() : removeDark();
  });
})();
