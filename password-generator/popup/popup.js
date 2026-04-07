

// === OmniSuite Pro Upsell (usage-gated) ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const PRO_KEY = 'ma_pro_dismissed';
  const PRO_BOUGHT_KEY = 'ma_pro_active';

  _api.storage.local.get([PRO_KEY, PRO_BOUGHT_KEY, 'secure_password_generator_usage'], (r) => {
    if (r[PRO_BOUGHT_KEY] || r[PRO_KEY]) return;
    const usage = r['secure_password_generator_usage'] || 0;
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
  const EXT_ID = 'secure_password_generator';
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

const pw=document.getElementById('pw'),len=document.getElementById('len'),lenVal=document.getElementById('lenVal');
function gen(){let chars='';if(document.getElementById('upper').checked)chars+='ABCDEFGHIJKLMNOPQRSTUVWXYZ';if(document.getElementById('lower').checked)chars+='abcdefghijklmnopqrstuvwxyz';if(document.getElementById('nums').checked)chars+='0123456789';if(document.getElementById('syms').checked)chars+='!@#$%^&*()_+-=[]{}|;:,.<>?';if(!chars)chars='abcdefghijklmnopqrstuvwxyz';const a=new Uint32Array(parseInt(len.value));crypto.getRandomValues(a);pw.textContent=Array.from(a).map(v=>chars[v%chars.length]).join('');}
len.oninput=()=>{lenVal.textContent=len.value;gen();};
pw.onclick=()=>navigator.clipboard.writeText(pw.textContent).then(()=>{const o=pw.textContent;pw.textContent='✅ Copied!';pw.style.color='#a855f7';setTimeout(()=>{pw.textContent=o;pw.style.color='#4ade80';},1200);});
document.getElementById('genBtn').onclick=gen;['upper','lower','nums','syms'].forEach(id=>document.getElementById(id).onchange=gen);gen();
