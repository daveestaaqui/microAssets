
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'css_inspector_pro';
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

let uses=0,lastCSS='';
document.getElementById('inspectBtn').onclick=()=>{chrome.storage.local.get(['omnisuite_pro_key_css-inspector-pro'],d=>{uses++;if(uses>5&&!d['omnisuite_pro_key_css-inspector-pro']){document.getElementById('gate').style.display='block';return;}
chrome.tabs.query({active:true,currentWindow:true},tabs=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:()=>{return new Promise(resolve=>{const overlay=document.createElement('div');overlay.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;z-index:999999;cursor:crosshair;';document.body.appendChild(overlay);overlay.onclick=e=>{e.preventDefault();e.stopPropagation();overlay.remove();const el=document.elementFromPoint(e.clientX,e.clientY);if(!el)return resolve(null);const cs=getComputedStyle(el);const props=['color','background-color','background','font-family','font-size','font-weight','line-height','letter-spacing','margin','padding','border','border-radius','width','height','display','position','top','right','bottom','left','flex','gap','grid','box-shadow','text-shadow','opacity','transform','transition','z-index','overflow','text-align','text-decoration','cursor'];
const result={tag:el.tagName.toLowerCase(),classes:el.className,id:el.id,styles:{}};props.forEach(p=>{const v=cs.getPropertyValue(p);if(v&&v!=='none'&&v!=='normal'&&v!=='0px'&&v!=='auto'&&v!=='visible'&&v!=='static'&&v!=='0s')result.styles[p]=v;});resolve(result);};});}}).then(r=>{const d=r[0].result;if(!d)return;const el=document.getElementById('results');
lastCSS=Object.entries(d.styles).map(([k,v])=>`${k}: ${v};`).join('\n');
el.innerHTML=`<div style="color:#c084fc;margin-bottom:6px;">&lt;${d.tag}${d.id?' #'+d.id:''}${d.classes?' .'+d.classes.split(' ').join('.'):''}&gt;</div>`+
Object.entries(d.styles).map(([k,v])=>`<div style="padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.03);"><span style="color:#7dd3fc;">${k}</span>: <span style="color:#fde68a;">${v}</span>;</div>`).join('');
document.getElementById('copyBtn').style.display='block';});});});};
document.getElementById('copyBtn').onclick=()=>navigator.clipboard.writeText(lastCSS);
