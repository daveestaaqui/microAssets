
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'lorem_ipsum_and_placeholder_text';
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

const words="lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua enim ad minim veniam quis nostrud exercitation ullamco laboris nisi aliquip ex ea commodo consequat duis aute irure in reprehenderit voluptate velit esse cillum fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt culpa qui officia deserunt mollit anim id est laborum".split(' ');
function rw(){return words[Math.floor(Math.random()*words.length)];}
function sentence(){const l=8+Math.floor(Math.random()*12);let s=Array.from({length:l},rw).join(' ');return s.charAt(0).toUpperCase()+s.slice(1)+'.';}
function paragraph(){return Array.from({length:4+Math.floor(Math.random()*4)},sentence).join(' ');}
document.getElementById('genBtn').onclick=()=>{const n=parseInt(document.getElementById('count').value)||3;const t=document.getElementById('type').value;let r;if(t==='paragraphs')r=Array.from({length:n},paragraph).join('\n\n');else if(t==='sentences')r=Array.from({length:n},sentence).join(' ');else r=Array.from({length:n},rw).join(' ');document.getElementById('output').value=r;};
document.getElementById('output').onclick=function(){navigator.clipboard.writeText(this.value).then(()=>{const o=this.value;this.value='✅ Copied!';setTimeout(()=>this.value=o,1200);});};
document.getElementById('genBtn').click();


// Review request after 5 uses
(function(){
  const key = 'flowkit_uses_' + chrome.runtime.id;
  const dismissed = 'flowkit_review_dismissed_' + chrome.runtime.id;
  chrome.storage.local.get([key, dismissed], r => {
    if (r[dismissed]) return;
    const uses = (r[key] || 0) + 1;
    chrome.storage.local.set({[key]: uses});
    if (uses === 5) {
      const banner = document.createElement('div');
      banner.innerHTML = '<div style="padding:8px 12px;background:#1a1a2e;border-bottom:1px solid #667eea;font-size:12px;color:#cdd6f4;text-align:center;">Enjoying this extension? <a href="https://chrome.google.com/webstore" target="_blank" style="color:#667eea;">Leave a review ⭐</a> <span id="flowkit-dismiss" style="cursor:pointer;margin-left:12px;color:#8b949e;">✕</span></div>';
      document.body.prepend(banner);
      document.getElementById('flowkit-dismiss').addEventListener('click', () => {
        banner.remove();
        chrome.storage.local.set({[dismissed]: true});
      });
    }
  });
})();
