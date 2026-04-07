

// === OmniSuite Pro Upsell (usage-gated) ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const PRO_KEY = 'ma_pro_dismissed';
  const PRO_BOUGHT_KEY = 'ma_pro_active';

  _api.storage.local.get([PRO_KEY, PRO_BOUGHT_KEY, 'site_speed_analyzer_usage'], (r) => {
    if (r[PRO_BOUGHT_KEY] || r[PRO_KEY]) return;
    const usage = r['site_speed_analyzer_usage'] || 0;
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
  const EXT_ID = 'site_speed_analyzer';
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

document.getElementById('analyzeBtn').onclick=()=>{chrome.tabs.query({active:true,currentWindow:true},(tabs)=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:()=>{const p=performance.getEntriesByType('navigation')[0];const r=performance.getEntriesByType('resource');return{url:location.href,domElements:document.querySelectorAll('*').length,resourceCount:r.length,totalSize:r.reduce((a,e)=>a+(e.transferSize||0),0),loadTime:Math.round(p.loadEventEnd-p.startTime),domContentLoaded:Math.round(p.domContentLoadedEventEnd-p.startTime),ttfb:Math.round(p.responseStart-p.startTime),images:document.images.length,scripts:document.scripts.length,stylesheets:document.styleSheets.length};}}).then(results=>{const d=results[0].result;const el=document.getElementById('results');
const grade=d.loadTime<1000?{l:'A',c:'#4ade80'}:d.loadTime<2500?{l:'B',c:'#facc15'}:d.loadTime<4000?{l:'C',c:'#fb923c'}:{l:'F',c:'#f87171'};
el.innerHTML=`<div style="text-align:center;margin-bottom:12px;"><span style="font-size:48px;font-weight:bold;color:${grade.c};">${grade.l}</span><br><span style="color:#a1a1aa;font-size:11px;">Performance Grade</span></div>`+
[['⏱️ Load Time',d.loadTime+'ms'],['📄 DOM Elements',d.domElements.toLocaleString()],['📦 Resources',d.resourceCount],['💾 Total Size',(d.totalSize/1024).toFixed(0)+'KB'],['⚡ TTFB',d.ttfb+'ms'],['📷 Images',d.images],['📜 Scripts',d.scripts],['🎨 Stylesheets',d.stylesheets]].map(([k,v])=>`<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.05);"><span style="color:#a1a1aa;">${k}</span><span style="color:#fafafa;font-weight:600;">${v}</span></div>`).join('');});});};
