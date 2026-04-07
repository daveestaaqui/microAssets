// Sponsor Skipper — auto-advance the video past sponsor segments
// Uses SponsorBlock-style segment markers from aria labels
(function() {
  'use strict';
  const KEY = 'sponsor_skipper_enabled';
  let enabled = true;

  chrome.storage.local.get([KEY], r => { enabled = r[KEY] !== false; });
  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE') enabled = msg.enabled;
  });

  function trySkip() {
    if (!enabled) return;
    // Look for YouTube's own "Skip Ad" / "Skip Intro" button
    const skipBtn = document.querySelector(
      '.ytp-skip-intro-button, .ytp-ad-skip-button, .ytp-ad-skip-button-modern'
    );
    if (skipBtn) { skipBtn.click(); return; }

    // Skip chapter-based segments marked as [Sponsor] in chapater list
    const video = document.querySelector('video');
    if (!video) return;
    const chapters = document.querySelectorAll('.ytp-chapter-hover-container');
    chapters.forEach(ch => {
      const label = (ch.getAttribute('aria-label') || '').toLowerCase();
      if (label.includes('sponsor') && !video.paused) {
        const end = parseFloat(ch.dataset.endSec);
        if (!isNaN(end) && video.currentTime < end) video.currentTime = end;
      }
    });
  }

  setInterval(trySkip, 1000);
})();
