
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'css_gradient_generator_and_picker';
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

const c1 = document.getElementById('c1');
const c2 = document.getElementById('c2');
const angle = document.getElementById('angle');
const angleVal = document.getElementById('angleVal');
const preview = document.getElementById('preview');
const cssOutput = document.getElementById('cssOutput');
const linearBtn = document.getElementById('linearBtn');
const radialBtn = document.getElementById('radialBtn');
let mode = 'linear';

function update() {
  let css;
  if (mode === 'linear') {
    css = `linear-gradient(${angle.value}deg, ${c1.value}, ${c2.value})`;
  } else {
    css = `radial-gradient(circle, ${c1.value}, ${c2.value})`;
  }
  preview.style.background = css;
  cssOutput.textContent = `background: ${css};`;
  angleVal.textContent = angle.value;
}

c1.addEventListener('input', update);
c2.addEventListener('input', update);
angle.addEventListener('input', update);

linearBtn.addEventListener('click', () => {
  mode = 'linear';
  linearBtn.style.opacity = '1';
  radialBtn.style.opacity = '0.5';
  update();
});

radialBtn.addEventListener('click', () => {
  mode = 'radial';
  radialBtn.style.opacity = '1';
  linearBtn.style.opacity = '0.5';
  update();
});

cssOutput.addEventListener('click', () => {
  navigator.clipboard.writeText(cssOutput.textContent).then(() => {
    const orig = cssOutput.textContent;
    cssOutput.textContent = '✅ Copied to clipboard!';
    setTimeout(() => { cssOutput.textContent = orig; }, 1500);
  });
});

update();
