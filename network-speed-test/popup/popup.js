
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'network_speed_test';
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
  const btn = document.getElementById('test');
  const output = document.getElementById('output');
  const progress = document.getElementById('progress');
  
  btn.onclick = async () => {
    btn.disabled = true;
    btn.textContent = 'Testing...';
    output.textContent = '';
    progress.style.width = '0%';
    
    try {
      // Test download speed using a public CDN file
      const testUrls = [
        'https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js', // ~87KB
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js', // ~60KB
      ];
      
      let totalBytes = 0;
      let totalTime = 0;
      
      for (let i = 0; i < testUrls.length; i++) {
        progress.style.width = ((i+1)/testUrls.length*100) + '%';
        const start = performance.now();
        const res = await fetch(testUrls[i] + '?t=' + Date.now(), {cache: 'no-store'});
        const blob = await res.blob();
        const end = performance.now();
        totalBytes += blob.size;
        totalTime += (end - start);
      }
      
      const mbps = ((totalBytes * 8) / (totalTime / 1000) / 1000000).toFixed(1);
      const color = mbps > 50 ? '#a6e3a1' : mbps > 10 ? '#f9e2af' : '#f38ba8';
      
      output.innerHTML = '<div style="text-align:center;"><div style="font-size:48px;font-weight:bold;color:'+color+';">'+mbps+'</div><div style="color:#888;font-size:14px;">Mbps download</div><div style="color:#585858;font-size:11px;margin-top:8px;">Tested '+Math.round(totalBytes/1024)+'KB in '+Math.round(totalTime)+'ms</div></div>';
    } catch(e) {
      output.innerHTML = '<div style="color:#f38ba8;text-align:center;">Test failed: ' + e.message + '</div>';
    }
    
    btn.disabled = false;
    btn.textContent = 'Test Again';
    progress.style.width = '100%';
  };
});