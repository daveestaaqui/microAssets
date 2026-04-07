
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'text_case_converter';
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

const inp=document.getElementById('input'),out=document.getElementById('output'),btns=document.getElementById('btns');
const cases={UPPER:s=>s.toUpperCase(),lower:s=>s.toLowerCase(),'Title Case':s=>s.replace(/\w\S*/g,t=>t.charAt(0).toUpperCase()+t.substr(1).toLowerCase()),camelCase:s=>s.toLowerCase().replace(/[^a-zA-Z0-9]+(.)/g,(_,c)=>c.toUpperCase()),snake_case:s=>s.toLowerCase().replace(/\s+/g,'_').replace(/[^a-z0-9_]/g,''),'kebab-case':s=>s.toLowerCase().replace(/\s+/g,'-').replace(/[^a-z0-9-]/g,''),'dot.case':s=>s.toLowerCase().replace(/\s+/g,'.').replace(/[^a-z0-9.]/g,''),Reverse:s=>s.split('').reverse().join('')};
Object.entries(cases).forEach(([name,fn])=>{const b=document.createElement('button');b.textContent=name;b.className='sdal-btn';b.style.cssText='font-size:10px;padding:5px 2px;opacity:0.8;';b.onclick=()=>{out.value=fn(inp.value);};btns.appendChild(b);});
out.onclick=function(){navigator.clipboard.writeText(this.value).then(()=>{const o=this.value;this.value='✅ Copied!';setTimeout(()=>this.value=o,1200);});};
