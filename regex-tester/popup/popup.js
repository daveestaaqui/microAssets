

// === OmniSuite Pro Upsell (usage-gated) ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const PRO_KEY = 'ma_pro_dismissed';
  const PRO_BOUGHT_KEY = 'ma_pro_active';

  _api.storage.local.get([PRO_KEY, PRO_BOUGHT_KEY, 'regex_tester_and_debugger_usage'], (r) => {
    if (r[PRO_BOUGHT_KEY] || r[PRO_KEY]) return;
    const usage = r['regex_tester_and_debugger_usage'] || 0;
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
  const EXT_ID = 'regex_tester_and_debugger';
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

const pattern=document.getElementById('pattern'),testStr=document.getElementById('testStr'),result=document.getElementById('matchResult'),flagG=document.getElementById('flagG'),flagI=document.getElementById('flagI'),flagM=document.getElementById('flagM');
function test(){try{const f=(flagG.checked?'g':'')+(flagI.checked?'i':'')+(flagM.checked?'m':'');const re=new RegExp(pattern.value,f);const m=testStr.value.match(re);if(m){result.innerHTML='<span style="color:#4ade80">'+m.length+' match'+(m.length>1?'es':'')+':</span> '+m.map(x=>'<code style="background:rgba(168,85,247,0.2);padding:1px 4px;border-radius:3px;">'+x+'</code>').join(' ');}else{result.innerHTML='<span style="color:#f87171">No matches</span>';}}catch(e){result.innerHTML='<span style="color:#f87171">'+e.message+'</span>';}}
pattern.addEventListener('input',test);testStr.addEventListener('input',test);flagG.addEventListener('change',test);flagI.addEventListener('change',test);flagM.addEventListener('change',test);
