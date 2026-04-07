// Reading Time Badge — estimates reading time and sends to background badge
(function() {
  'use strict';
  const KEY = 'reading_badge_enabled';
  const WPM = 238; // average adult reading speed

  function countWords() {
    const main = document.querySelector('article, [role="main"], main, .post-content, .entry-content')
      || document.body;
    const text = main.innerText || main.textContent || '';
    return text.trim().split(/\s+/).filter(Boolean).length;
  }

  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    const words = countWords();
    const minutes = Math.max(1, Math.round(words / WPM));
    chrome.runtime.sendMessage({ type: 'SET_BADGE', text: `${minutes}m` }).catch(() => {});
  });
})();
