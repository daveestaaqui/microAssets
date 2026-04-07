// Pomodoro Anywhere — shows a floating countdown widget on all pages
(function() {
  'use strict';
  const KEY = 'pomodoro_enabled';

  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
  });

  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'POMODORO_START') {
      showWidget(msg.seconds || 1500);
    }
  });

  function showWidget(totalSecs) {
    const existing = document.getElementById('__sdal_pomodoro__');
    if (existing) existing.remove();

    const div = document.createElement('div');
    div.id = '__sdal_pomodoro__';
    div.style.cssText = `
      position:fixed; bottom:20px; right:20px; z-index:2147483647;
      background: linear-gradient(135deg,#1e1e2e,#2d1044);
      border: 1px solid #A855F755; border-radius: 12px;
      padding: 10px 16px; color: #e0e0e0; font-family: monospace;
      font-size: 22px; font-weight: bold; box-shadow: 0 4px 24px #0008;
      cursor: move; user-select: none;
    `;
    document.body.appendChild(div);

    let remaining = totalSecs;
    const t = setInterval(() => {
      if (remaining <= 0) {
        clearInterval(t);
        div.textContent = '🍅 Done!';
        setTimeout(() => div.remove(), 3000);
        return;
      }
      const m = String(Math.floor(remaining / 60)).padStart(2,'0');
      const s = String(remaining % 60).padStart(2,'0');
      div.textContent = `🍅 ${m}:${s}`;
      remaining--;
    }, 1000);
  }
})();
