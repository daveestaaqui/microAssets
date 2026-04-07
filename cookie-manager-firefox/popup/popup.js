
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'cookie_manager_and_viewer';
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
  const rateLink = document.getElementById('ma-rate');
  if (rateLink) {
    try {
      const id = _api.runtime.id;
      rateLink.href = 'https://chrome.google.com/webstore/detail/' + id + '/reviews';
    } catch (e) { console.error("Caught error:", e); }
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

function load(filter=''){chrome.tabs.query({active:true,currentWindow:true},tabs=>{const url=new URL(tabs[0].url);chrome.cookies.getAll({domain:url.hostname},cookies=>{const filtered=filter?cookies.filter(c=>c.name.toLowerCase().includes(filter)||c.value.toLowerCase().includes(filter)):cookies;document.getElementById('count').textContent=filtered.length+' cookies for '+url.hostname;const el=document.getElementById('cookies');el.innerHTML=filtered.map(c=>`<div style="padding:4px;margin-bottom:2px;border-radius:4px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);"><div style="display:flex;justify-content:space-between;"><span style="color:#7dd3fc;font-weight:600;font-size:10px;">${c.name}</span><span style="color:#f87171;font-size:9px;cursor:pointer;" data-name="${c.name}" data-url="${url.protocol}//${c.domain}${c.path}" class="del">✕</span></div><div style="color:#a1a1aa;font-size:9px;overflow:hidden;max-height:20px;">${c.value.slice(0,80)}</div><div style="color:#52525b;font-size:8px;margin-top:1px;">${c.secure?'🔒':''}${c.httpOnly?' HTTP':''}${c.session?' Session':' Expires: '+new Date(c.expirationDate*1000).toLocaleDateString()}</div></div>`).join('');el.querySelectorAll('.del').forEach(b=>b.onclick=()=>{chrome.cookies.remove({url:b.dataset.url,name:b.dataset.name},()=>load(filter));});});});};
document.getElementById('search').addEventListener('input',e=>load(e.target.value.toLowerCase()));
document.getElementById('clearAll').onclick=()=>{if(confirm('Delete all cookies for this site?')){chrome.tabs.query({active:true,currentWindow:true},tabs=>{const url=new URL(tabs[0].url);chrome.cookies.getAll({domain:url.hostname},cookies=>{cookies.forEach(c=>chrome.cookies.remove({url:url.protocol+'//'+c.domain+c.path,name:c.name}));setTimeout(()=>load(),300);});});}};load();
