
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'meta_tag_viewer_and_editor';
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

document.getElementById('scanBtn').onclick=()=>{chrome.tabs.query({active:true,currentWindow:true},(tabs)=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:()=>{const metas=[];document.querySelectorAll('meta').forEach(m=>{const name=m.getAttribute('name')||m.getAttribute('property')||m.getAttribute('http-equiv')||'';const content=m.getAttribute('content')||'';if(name||content)metas.push({name,content});});return{title:document.title,url:location.href,canonical:document.querySelector('link[rel=canonical]')?.href||'',metas};}}).then(results=>{const d=results[0].result;const el=document.getElementById('tags');
const sections=[{title:'📄 Basic',items:[['Title',d.title],['URL',d.url],['Canonical',d.canonical||'❌ Missing']]},{title:'📱 Open Graph',items:d.metas.filter(m=>m.name.startsWith('og:')).map(m=>[m.name,m.content])},{title:'🐦 Twitter',items:d.metas.filter(m=>m.name.startsWith('twitter:')).map(m=>[m.name,m.content])},{title:'🔍 SEO',items:d.metas.filter(m=>['description','keywords','robots','author','viewport'].includes(m.name)).map(m=>[m.name,m.content])},{title:'📋 Other',items:d.metas.filter(m=>!m.name.startsWith('og:')&&!m.name.startsWith('twitter:')&&!['description','keywords','robots','author','viewport'].includes(m.name)&&m.name).map(m=>[m.name,m.content])}];
el.innerHTML=sections.filter(s=>s.items.length).map(s=>`<div style="margin-bottom:10px;"><h4 style="color:#c084fc;font-size:12px;font-weight:600;margin-bottom:4px;">${s.title}</h4>`+s.items.map(([k,v])=>`<div style="display:flex;gap:6px;padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.03);"><span style="color:#71717a;min-width:80px;flex-shrink:0;">${k}</span><span style="color:#d4d4d8;word-break:break-all;">${v}</span></div>`).join('')+'</div>').join('');});});};
