
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'timestamp_converter';
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

const nowEl=document.getElementById('now'),input=document.getElementById('input'),output=document.getElementById('output');
function updateClock(){const n=new Date();const ts=Math.floor(n.getTime()/1000);nowEl.innerHTML='<div style="font-size:14px;font-weight:700;">'+n.toLocaleString()+'</div><div style="font-size:10px;color:#a1a1aa;">Unix: '+ts+'</div>';nowEl.onclick=function(){navigator.clipboard.writeText(String(ts));nowEl.style.borderColor='rgba(74,222,128,0.5)';setTimeout(function(){nowEl.style.borderColor='rgba(168,85,247,0.2)';},500);};}
updateClock();setInterval(updateClock,1000);
function convert(){var v=input.value.trim();if(!v){output.textContent = '';return;}
var d;if(/^\d{10}$/.test(v))d=new Date(parseInt(v)*1000);else if(/^\d{13}$/.test(v))d=new Date(parseInt(v));else d=new Date(v);
if(isNaN(d)){output.innerHTML='<span style="color:#f87171;">Invalid input</span>';return;}
var ts=Math.floor(d.getTime()/1000);
var diff=Date.now()-d.getTime();var abs=Math.abs(diff);var s=abs/1000;var rel;if(s<60)rel=Math.round(s)+'s ago';else if(s<3600)rel=Math.round(s/60)+'m ago';else if(s<86400)rel=Math.round(s/3600)+'h ago';else rel=Math.round(s/86400)+'d ago';
output.innerHTML='<div style="padding:3px 0;"><span style="color:#a855f7;font-size:10px;">Unix (s):</span> <span style="color:#d4d4d8;">'+ts+'</span></div><div style="padding:3px 0;"><span style="color:#a855f7;font-size:10px;">ISO 8601:</span> <span style="color:#d4d4d8;">'+d.toISOString()+'</span></div><div style="padding:3px 0;"><span style="color:#a855f7;font-size:10px;">Local:</span> <span style="color:#d4d4d8;">'+d.toLocaleString()+'</span></div><div style="padding:3px 0;"><span style="color:#a855f7;font-size:10px;">UTC:</span> <span style="color:#d4d4d8;">'+d.toUTCString()+'</span></div><div style="padding:3px 0;"><span style="color:#a855f7;font-size:10px;">Relative:</span> <span style="color:#d4d4d8;">'+rel+'</span></div>';}
input.addEventListener('input',convert);
