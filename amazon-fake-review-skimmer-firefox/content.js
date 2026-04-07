// Amazon Fake Review Skimmer
(function() {
  'use strict';
  const KEY = 'fake_review_enabled';
  chrome.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    const FAKE_SIGNALS = [
      /received.*(free|discount|compli)/i,
      /in exchange for.*(honest|unbiased)/i,
      /love.*(this|it).*so much/i,
      /best.*ever.*bought/i,
      /highly recommend/i,
      /five stars?/i,
      /amazing product/i,
    ];
    function scanReviews() {
      document.querySelectorAll('[data-hook="review"], .a-section.review').forEach(review => {
        if (review.dataset.scanned) return;
        review.dataset.scanned = '1';
        const text = review.textContent || '';
        let score = 0;
        for (const re of FAKE_SIGNALS) {
          if (re.test(text)) score++;
        }
        // Check review length (very short + 5 star = suspicious)
        if (text.length < 100) score++;
        // Check for verified purchase
        if (!text.includes('Verified Purchase')) score++;
        if (score >= 3) {
          review.style.borderLeft = '3px solid #f87171';
          review.style.opacity = '0.6';
          const badge = document.createElement('div');
          badge.style.cssText = 'background:#f87171;color:white;padding:2px 8px;font-size:11px;border-radius:4px;display:inline-block;margin:4px 0;';
          badge.textContent = '⚠ Possibly Fake (' + score + ' signals)';
          review.prepend(badge);
        }
      });
    }
    setTimeout(scanReviews, 2000);
    const obs = new MutationObserver(scanReviews);
    obs.observe(document.body || document.documentElement, { childList: true, subtree: true });
  });
  chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === 'TOGGLE') location.reload();
  });
})();
