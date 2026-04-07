
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'invoice_data_extractor_to_csv';
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

const KEY_STORAGE = 'invoice_license';
const ENABLED_KEY = 'invoice_enabled';

const toggle = document.getElementById('toggleSwitch');
const licenseInput = document.getElementById('licenseInput');
const activateBtn = document.getElementById('activateBtn');
const licenseStatus = document.getElementById('licenseStatus');
const licenseText = document.getElementById('licenseText');

// Validate format (any 4 groups of 4 alphanumeric chars)
function isValidFormat(key) {
  return /^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/i.test(key.trim());
}

chrome.storage.local.get([KEY_STORAGE, ENABLED_KEY], (r) => {
  toggle.checked = r[ENABLED_KEY] !== false;
  if (r[KEY_STORAGE]) {
    licenseInput.value = r[KEY_STORAGE];
    setActivated(r[KEY_STORAGE]);
  }
});

function setActivated(key) {
  licenseStatus.classList.add('active');
  licenseText.textContent = '✅ Licensed: ' + key.substring(0, 9) + '...';
}

activateBtn.addEventListener('click', () => {
  const key = licenseInput.value.trim().toUpperCase();
  if (isValidFormat(key)) {
    chrome.storage.local.set({ [KEY_STORAGE]: key });
    setActivated(key);
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) chrome.tabs.sendMessage(tabs[0].id, { type: 'TOGGLE', enabled: true }).catch(() => {});
    });
  } else {
    licenseText.textContent = '❌ Invalid key format';
    licenseStatus.classList.remove('active');
  }
});

toggle.addEventListener('change', () => {
  chrome.storage.local.set({ [ENABLED_KEY]: toggle.checked });
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) chrome.tabs.sendMessage(tabs[0].id, { type: 'TOGGLE', enabled: toggle.checked }).catch(() => {});
  });
});
