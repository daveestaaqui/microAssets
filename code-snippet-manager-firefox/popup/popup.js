
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'code_snippet_manager_pro';
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

const MAX_FREE=10;
document.getElementById('addBtn').onclick=()=>{const f=document.getElementById('addForm');f.style.display=f.style.display==='none'?'block':'none';};
document.getElementById('saveBtn').onclick=()=>{const t=document.getElementById('title').value.trim(),tags=document.getElementById('tags').value.trim(),code=document.getElementById('code').value;if(!t||!code)return;
chrome.storage.local.get(['snippets','snippetsPro'],d=>{const s=d.snippets||[];if(s.length>=MAX_FREE&&!d.snippetsPro){document.getElementById('gate').style.display='block';return;}
s.unshift({title:t,tags:tags.split(',').map(x=>x.trim()).filter(Boolean),code,ts:Date.now()});chrome.storage.local.set({snippets:s},()=>{document.getElementById('addForm').style.display='none';document.getElementById('title').value='';document.getElementById('tags').value='';document.getElementById('code').value='';render();});});};
function render(filter=''){chrome.storage.local.get(['snippets'],d=>{const s=(d.snippets||[]).filter(x=>!filter||x.title.toLowerCase().includes(filter)||x.tags.some(t=>t.toLowerCase().includes(filter)));const el=document.getElementById('snippets');if(!s.length){el.innerHTML='<p style="color:#71717a;text-align:center;padding:16px;">No snippets yet</p>';return;}
el.innerHTML=s.map((x,i)=>`<div style="padding:6px;margin-bottom:4px;border-radius:6px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);"><div style="display:flex;justify-content:space-between;"><span style="color:#fafafa;font-weight:600;font-size:12px;">${x.title}</span><span style="color:#71717a;font-size:10px;cursor:pointer;" onclick="del(${i})">✕</span></div>${x.tags.length?'<div style="margin:2px 0;">'+x.tags.map(t=>'<span style="display:inline-block;padding:1px 4px;border-radius:3px;background:rgba(168,85,247,0.15);color:#c084fc;font-size:9px;margin-right:2px;">'+t+'</span>').join('')+'</div>':''}<pre style="padding:4px;border-radius:4px;background:rgba(0,0,0,0.3);color:#a5f3fc;font-size:10px;font-family:monospace;overflow:hidden;max-height:40px;cursor:pointer;" onclick="copy(${i})">${x.code.slice(0,200)}</pre></div>`).join('');});}
window.copy=i=>{chrome.storage.local.get(['snippets'],d=>{navigator.clipboard.writeText(d.snippets[i].code);});};
window.del=i=>{chrome.storage.local.get(['snippets'],d=>{d.snippets.splice(i,1);chrome.storage.local.set({snippets:d.snippets},render);});};
document.getElementById('search').addEventListener('input',e=>render(e.target.value.toLowerCase()));render();
