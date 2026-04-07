
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'api_tester_pro__rest_client';
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

const sendBtn=document.getElementById('sendBtn'),urlInput=document.getElementById('url'),method=document.getElementById('method'),headersInput=document.getElementById('headers'),bodyInput=document.getElementById('body'),statusEl=document.getElementById('status'),responseEl=document.getElementById('response');
let reqCount=0;
sendBtn.onclick=async()=>{
  chrome.storage.local.get(['apiTesterLicense'],async(d)=>{
    reqCount++;
    if(reqCount>5&&!d.apiTesterLicense){
      document.getElementById('licenseGate').style.display='block';return;
    }
    const u=urlInput.value.trim();if(!u){statusEl.textContent='⚠️ Enter a URL';return;}
    statusEl.innerHTML='<span style="color:#facc15">⏳ Sending...</span>';
    const start=performance.now();
    try{
      const opts={method:method.value};
      if(headersInput.value.trim()){opts.headers=JSON.parse(headersInput.value);}
      if(['POST','PUT','PATCH'].includes(method.value)&&bodyInput.value.trim()){opts.body=bodyInput.value;}
      const r=await fetch(u,opts);const elapsed=Math.round(performance.now()-start);
      const text=await r.text();let display;
      try{display=JSON.stringify(JSON.parse(text),null,2);}catch(e){display=text;}
      statusEl.innerHTML=`<span style="color:${r.ok?'#4ade80':'#f87171'}">${r.status} ${r.statusText}</span> · ${elapsed}ms · ${(text.length/1024).toFixed(1)}KB`;
      responseEl.textContent=display;
    }catch(e){statusEl.innerHTML='<span style="color:#f87171">Error</span>';responseEl.textContent=e.message;}
  });
};
document.getElementById('activateBtn')?.addEventListener('click',()=>{
  const key=document.getElementById('licenseKey').value.trim();
  if(key.length>=8){chrome.storage.local.set({apiTesterLicense:key});document.getElementById('licenseGate').style.display='none';statusEl.textContent='✅ License activated!';}
});
