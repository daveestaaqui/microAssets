
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'website_change_monitor_pro';
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

const MAX_FREE=2;
document.getElementById('addBtn').onclick=()=>{const url=document.getElementById('url').value.trim();const mins=parseInt(document.getElementById('interval').value);if(!url)return;
chrome.storage.local.get(['monitors','monitorPro'],d=>{const m=d.monitors||{};if(Object.keys(m).length>=MAX_FREE&&!d.monitorPro){document.getElementById('gate').style.display='block';return;}
m[url]={interval:mins,added:Date.now(),lastCheck:null,hash:null,changed:false};chrome.storage.local.set({monitors:m},()=>{chrome.alarms.create('monitor_'+url,{periodInMinutes:mins});document.getElementById('url').value='';render();});});};
function render(){chrome.storage.local.get(['monitors'],d=>{const m=d.monitors||{};const el=document.getElementById('monitors');const urls=Object.keys(m);if(!urls.length){el.innerHTML='<p style="color:#71717a;text-align:center;padding:16px;">No monitors set up</p>';return;}
el.innerHTML=urls.map(url=>{const x=m[url];return `<div style="padding:6px;margin-bottom:4px;border-radius:6px;background:rgba(255,255,255,0.03);border:1px solid ${x.changed?'rgba(74,222,128,0.3)':'rgba(255,255,255,0.05)'};"><div style="display:flex;justify-content:space-between;"><span style="color:#d4d4d8;font-size:11px;overflow:hidden;flex:1;">${url.slice(0,40)}…</span><span style="color:#71717a;font-size:10px;cursor:pointer;" data-url="${url}" class="del">✕</span></div><div style="display:flex;justify-content:space-between;margin-top:2px;"><span style="color:#71717a;font-size:10px;">Every ${x.interval}m</span><span style="font-size:10px;color:${x.changed?'#4ade80':'#71717a'};">${x.changed?'🟢 Changed!':'⏳ Monitoring'}</span></div></div>`;}).join('');
el.querySelectorAll('.del').forEach(b=>b.onclick=()=>{const url=b.dataset.url;chrome.alarms.clear('monitor_'+url);chrome.storage.local.get(['monitors'],d=>{delete d.monitors[url];chrome.storage.local.set({monitors:d.monitors},render);});});});}render();
