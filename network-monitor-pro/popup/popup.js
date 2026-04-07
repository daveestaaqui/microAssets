
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'network_request_monitor_pro';
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

let uses=0;
function load(){chrome.tabs.query({active:true,currentWindow:true},tabs=>{chrome.runtime.sendMessage({type:'getRequests',tabId:tabs[0].id},reqs=>{if(!reqs)return;const filter=document.getElementById('filter').value;const filtered=filter?reqs.filter(r=>r.type===filter):reqs;
const stats=document.getElementById('stats');const total=filtered.length;const errors=filtered.filter(r=>r.status>=400).length;stats.innerHTML=`<span style="color:#4ade80;">${total} requests</span><span style="color:${errors?'#f87171':'#71717a'};">${errors} errors</span>`;
const el=document.getElementById('requests');el.innerHTML=filtered.reverse().map(r=>{const sc=r.status<300?'#4ade80':r.status<400?'#facc15':'#f87171';const url=new URL(r.url).pathname.slice(0,40);return `<div style="padding:3px 4px;border-bottom:1px solid rgba(255,255,255,0.03);display:flex;gap:6px;align-items:center;"><span style="color:${sc};min-width:24px;">${r.status}</span><span style="color:#71717a;min-width:28px;">${r.type.slice(0,4)}</span><span style="color:#d4d4d8;flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;" title="${r.url}">${url}</span></div>`;}).join('');});});}
document.getElementById('refreshBtn').onclick=()=>{chrome.storage.local.get(['omnisuite_pro_key_network-monitor-pro'],d=>{uses++;if(uses>10&&!d['omnisuite_pro_key_network-monitor-pro']){document.getElementById('gate').style.display='block';return;}load();});};
document.getElementById('filter').onchange=load;load();
