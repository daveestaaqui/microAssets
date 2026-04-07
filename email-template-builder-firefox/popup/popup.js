
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'email_template_builder_pro';
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

const MAX_FREE=3,sel=document.getElementById('templates'),preview=document.getElementById('preview');
const defaults=[{name:'Follow Up',body:'Hi {{name}},\n\nJust following up on our conversation about {{topic}}. Would love to schedule a quick call this week.\n\nBest,\n{{sender}}'},{name:'Introduction',body:'Hi {{name}},\n\nI\'m {{sender}} from {{company}}. I noticed your work on {{topic}} and would love to connect.\n\nBest regards,\n{{sender}}'},{name:'Thank You',body:'Hi {{name}},\n\nThank you for {{reason}}. I truly appreciate your time and effort.\n\nWarm regards,\n{{sender}}'}];
function load(){chrome.storage.local.get(['emailTemplates'],d=>{const tpls=d.emailTemplates||defaults;sel.textContent = '';tpls.forEach((t,i)=>{const o=document.createElement('option');o.value=i;o.textContent=t.name;sel.appendChild(o);});show(0);if(!d.emailTemplates)chrome.storage.local.set({emailTemplates:defaults});});}
function show(i){chrome.storage.local.get(['emailTemplates'],d=>{const t=(d.emailTemplates||defaults)[i];if(t)preview.textContent=t.body;});}
sel.onchange=()=>show(parseInt(sel.value));
document.getElementById('newBtn').onclick=()=>{chrome.storage.local.get(['emailTemplates','emailPro'],d=>{const t=d.emailTemplates||defaults;if(t.length>=MAX_FREE&&!d.emailPro){document.getElementById('gate').style.display='block';return;}document.getElementById('editor').style.display='block';});};
document.getElementById('saveTpl').onclick=()=>{const name=document.getElementById('tplName').value.trim(),body=document.getElementById('tplBody').value;if(!name||!body)return;chrome.storage.local.get(['emailTemplates'],d=>{const t=d.emailTemplates||defaults;t.push({name,body});chrome.storage.local.set({emailTemplates:t},()=>{document.getElementById('editor').style.display='none';document.getElementById('tplName').value='';document.getElementById('tplBody').value='';load();});});};
document.getElementById('copyBtn').onclick=()=>navigator.clipboard.writeText(preview.textContent);
document.getElementById('deleteBtn').onclick=()=>{const i=parseInt(sel.value);chrome.storage.local.get(['emailTemplates'],d=>{const t=d.emailTemplates||defaults;t.splice(i,1);chrome.storage.local.set({emailTemplates:t},load);});};load();
