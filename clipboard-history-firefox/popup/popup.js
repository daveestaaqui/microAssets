

// === OmniSuite Pro Upsell (usage-gated) ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const PRO_KEY = 'ma_pro_dismissed';
  const PRO_BOUGHT_KEY = 'ma_pro_active';

  _api.storage.local.get([PRO_KEY, PRO_BOUGHT_KEY, 'clipboard_history_manager_usage'], (r) => {
    if (r[PRO_BOUGHT_KEY] || r[PRO_KEY]) return;
    const usage = r['clipboard_history_manager_usage'] || 0;
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
  const EXT_ID = 'clipboard_history_manager';
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

const itemsDiv=document.getElementById('items'),searchInput=document.getElementById('search');
function render(filter=''){chrome.storage.local.get(['clipHistory'],(d)=>{const hist=d.clipHistory||[];itemsDiv.textContent = '';const filtered=filter?hist.filter(h=>h.text.toLowerCase().includes(filter)):hist;if(!filtered.length){itemsDiv.innerHTML='<p style="color:#71717a;text-align:center;padding:20px;">No items yet. Copy something!</p>';return;}
filtered.forEach((item,i)=>{const el=document.createElement('div');el.style.cssText='padding:6px 8px;border-radius:6px;margin-bottom:3px;background:rgba(255,255,255,0.03);cursor:pointer;transition:background 0.15s;display:flex;justify-content:space-between;align-items:center;';el.onmouseenter=()=>el.style.background='rgba(255,255,255,0.08)';el.onmouseleave=()=>el.style.background='rgba(255,255,255,0.03)';
const text=document.createElement('span');text.textContent=item.text.length>60?item.text.slice(0,60)+'…':item.text;text.style.cssText='color:#d4d4d8;flex:1;overflow:hidden;';
const time=document.createElement('span');time.textContent=new Date(item.ts).toLocaleTimeString();time.style.cssText='color:#52525b;font-size:10px;margin-left:8px;';
el.appendChild(text);el.appendChild(time);el.onclick=()=>navigator.clipboard.writeText(item.text).then(()=>{text.textContent='✅ Copied!';setTimeout(()=>text.textContent=item.text.length>60?item.text.slice(0,60)+'…':item.text,1200);});
itemsDiv.appendChild(el);})});}
document.getElementById('pasteBtn').onclick=()=>navigator.clipboard.readText().then(t=>{if(!t)return;chrome.storage.local.get(['clipHistory'],(d)=>{const h=d.clipHistory||[];h.unshift({text:t,ts:Date.now()});if(h.length>50)h.length=50;chrome.storage.local.set({clipHistory:h},()=>render());});});
document.getElementById('clearBtn').onclick=()=>chrome.storage.local.set({clipHistory:[]},()=>render());
searchInput.addEventListener('input',()=>render(searchInput.value.toLowerCase()));
render();
