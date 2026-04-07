

// === OmniSuite Pro Upsell (usage-gated) ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const PRO_KEY = 'ma_pro_dismissed';
  const PRO_BOUGHT_KEY = 'ma_pro_active';

  _api.storage.local.get([PRO_KEY, PRO_BOUGHT_KEY, 'qr_code_generator___instant_url_to_qr_usage'], (r) => {
    if (r[PRO_BOUGHT_KEY] || r[PRO_KEY]) return;
    const usage = r['qr_code_generator___instant_url_to_qr_usage'] || 0;
    if (usage >= 10) {
      const banner = document.getElementById('ma-pro-upsell');
      if (banner) banner.style.display = 'block';
    }
  });

  const dismissBtn = document.getElementById('ma-dismiss-pro');
  if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
      _api.storage.local.set({ [PRO_KEY]: true });
      const banner = document.getElementById('ma-pro-upsell');
      if (banner) banner.style.display = 'none';
    });
  }
})();

// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'qr_code_generator___instant_url_to_qr';
  const USAGE_KEY = EXT_ID + '_usage';

  // Track usage
  _api.storage.local.get([USAGE_KEY], (r) => {
    const count = ((r && r[USAGE_KEY]) || 0) + 1;
    _api.storage.local.set({ [USAGE_KEY]: count });
    // Show feedback prompt after 3 uses
    if (count >= 3) {
      const fb = document.getElementById('ma-feedback');
      if (fb) fb.style.display = 'block';
    }
  });

  // Wire up rate link
  // Smart Review Gate: Two-step satisfaction filter
  const rateLink = document.getElementById('ma-rate');
  if (rateLink) {
    rateLink.addEventListener('click', (e) => {
      e.preventDefault();
      const happy = confirm('Are you enjoying this extension? \n\nClick OK if yes, Cancel to send us feedback instead.');
      if (happy) {
        // Happy path → CWS review page
        try {
          const id = (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime.id : chrome.runtime.id;
          window.open('https://chrome.google.com/webstore/detail/' + id + '/reviews', '_blank');
        } catch(err) {
          window.open('https://chromewebstore.google.com/search/OmniSuite', '_blank');
        }
      } else {
        // Unhappy path → private feedback (funneled to AI support agent)
        window.open('mailto:support@sporlyworks.com?subject=Extension Feedback', '_blank');
      }
    });
  }

  // Global error handler
  window.addEventListener('error', (e) => {
    _api.storage.local.get(['ma_errors'], (r) => {
      const errors = (r && r.ma_errors) || [];
      errors.push({ ext: EXT_ID, msg: e.message, ts: Date.now() });
      if (errors.length > 20) errors.shift();
      _api.storage.local.set({ ma_errors: errors });
    });
  });
})();

const STORAGE_KEY = 'sdal_enabled';
const toggle = document.getElementById('toggleSwitch');
const qrInput = document.getElementById('qrInput');
const generateBtn = document.getElementById('generateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const canvas = document.getElementById('qrCanvas');

chrome.storage.local.get([STORAGE_KEY], (r) => {
  toggle.checked = r[STORAGE_KEY] !== false;
});

toggle.addEventListener('change', () => {
  chrome.storage.local.set({ [STORAGE_KEY]: toggle.checked });
});

// Get current tab URL on load
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (tabs[0]) qrInput.value = tabs[0].url;
});

// Simple QR code generator using the Google Charts API
generateBtn.addEventListener('click', () => {
  const text = qrInput.value.trim();
  if (!text) return;
  
  const size = 200;
  const img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = () => {
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, size, size);
    ctx.drawImage(img, 0, 0, size, size);
    canvas.style.display = 'block';
    downloadBtn.style.display = 'block';
  };
  img.src = `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${encodeURIComponent(text)}`;
});

downloadBtn.addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = 'qr-code.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
});
