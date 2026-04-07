
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'omnisuite_dev_toolkit';
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


document.addEventListener('DOMContentLoaded', () => {
  const btnWcag = document.getElementById('btn-wcag');
  const btnPrivacy = document.getElementById('btn-privacy');
  const btnContract = document.getElementById('btn-contract');
  const btnInvoice = document.getElementById('btn-invoice');
  
  chrome.storage.local.get(['suite_license'], r => {
      const hasLicense = !!r['suite_license'];
      document.getElementById('licenseText').textContent = hasLicense ? "Suite Unlocked & Active" : "Suite Locked - Enter Key";
      document.getElementById('licenseStatus').style.borderColor = hasLicense ? "#238636" : "#30363d";
      if(hasLicense) {
          document.getElementById('licenseInput').style.display = 'none';
          document.getElementById('activateBtn').style.display = 'none';
      }
  });

  document.getElementById('activateBtn').addEventListener('click', () => {
    const key = document.getElementById('licenseInput').value;
    if (key.length >= 8) {
      chrome.storage.local.set({ suite_license: key }, () => window.close());
    }
  });

  btnWcag.addEventListener('click', () => {
    chrome.tabs.query({active: true, currentWindow: true}, tabs => {
      chrome.tabs.sendMessage(tabs[0].id, {type: 'RUN_AUDIT'}, res => {
          if (res) alert(`WCAG Audit Complete! Found ${res.issues.length} issues.`);
      });
    });
  });

  btnPrivacy.addEventListener('click', () => {
    chrome.tabs.query({active: true, currentWindow: true}, tabs => {
      chrome.tabs.sendMessage(tabs[0].id, {type: 'PRIVACY_SCAN'}, res => {
          if (res) alert(`Privacy Score: ${res.score}/100. Found ${res.trackers.length} third-party trackers.`);
      });
    });
  });

  btnContract.addEventListener('click', () => {
    chrome.tabs.query({active: true, currentWindow: true}, tabs => {
      chrome.tabs.sendMessage(tabs[0].id, {type: 'TOGGLE', enabled: true});
      window.close();
    });
  });

  btnInvoice.addEventListener('click', () => {
    chrome.tabs.query({active: true, currentWindow: true}, tabs => {
      chrome.tabs.sendMessage(tabs[0].id, {type: 'EXTRACT_INVOICE'}, res => {
          if (res) alert(`Found ${res.amounts.length} monetary amounts on this invoice.`);
      });
    });
  });
});
