
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'html_table_to_csv_extractor';
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

document.getElementById('scanBtn').onclick=()=>{chrome.tabs.query({active:true,currentWindow:true},(tabs)=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:()=>{const tables=document.querySelectorAll('table');return Array.from(tables).map((t,i)=>{const rows=Array.from(t.rows).map(r=>Array.from(r.cells).map(c=>c.textContent.trim()));return{index:i,rows:rows.length,cols:rows[0]?.length||0,preview:rows.slice(0,2).map(r=>r.join(' | ')).join(' \\n '),csv:rows.map(r=>r.map(c=>c.includes(',')?'"'+c+'"':c).join(',')).join('\\n')};});}}).then(results=>{const tables=results[0].result;const el=document.getElementById('tables');if(!tables.length){el.innerHTML='<p style="color:#71717a;text-align:center;padding:20px;">No tables found on this page</p>';return;}
el.innerHTML=tables.map((t,i)=>'<div style="padding:8px;margin-bottom:6px;border-radius:8px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);"><div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span style="color:#c084fc;font-weight:600;">Table '+(i+1)+'</span><span style="color:#71717a;">'+t.rows+' rows × '+t.cols+' cols</span></div><pre style="color:#a1a1aa;font-size:10px;overflow:hidden;max-height:30px;">'+t.preview+'</pre><button class="sdal-btn" style="width:100%;margin-top:4px;font-size:11px;padding:4px;" onclick="navigator.clipboard.writeText(decodeURIComponent(atob(\''+btoa(encodeURIComponent(t.csv))+'\')))">📋 Copy as CSV</button></div>').join('');});});};
