
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'responsive_viewport_tester';
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

const sizes=[{name:'📱 iPhone SE',w:375,h:667},{name:'📱 iPhone 14',w:390,h:844},{name:'📱 Pixel 7',w:412,h:915},{name:'📱 Galaxy S21',w:360,h:800},{name:'📋 iPad Mini',w:768,h:1024},{name:'📋 iPad Air',w:820,h:1180},{name:'📋 iPad Pro',w:1024,h:1366},{name:'🖥️ Laptop',w:1366,h:768},{name:'🖥️ Desktop',w:1920,h:1080},{name:'🖥️ 4K',w:2560,h:1440}];
const container=document.getElementById('sizes');sizes.forEach(s=>{const btn=document.createElement('button');btn.className='sdal-btn';btn.style.cssText='font-size:10px;padding:6px 4px;opacity:0.8;text-align:left;';btn.innerHTML=`${s.name}<br><span style="color:#71717a;">${s.w}×${s.h}</span>`;btn.onclick=()=>{chrome.windows.getCurrent(win=>{chrome.windows.update(win.id,{width:s.w+16,height:s.h+88});});};container.appendChild(btn);});
