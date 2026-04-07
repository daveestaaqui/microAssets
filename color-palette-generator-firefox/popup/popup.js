
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'color_palette_generator';
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

function hexToHsl(hex){let r=parseInt(hex.slice(1,3),16)/255,g=parseInt(hex.slice(3,5),16)/255,b=parseInt(hex.slice(5,7),16)/255;let max=Math.max(r,g,b),min=Math.min(r,g,b),h,s,l=(max+min)/2;if(max===min){h=s=0;}else{let d=max-min;s=l>0.5?d/(2-max-min):d/(max+min);switch(max){case r:h=((g-b)/d+(g<b?6:0))/6;break;case g:h=((b-r)/d+2)/6;break;case b:h=((r-g)/d+4)/6;break;}}return[h*360,s*100,l*100];}
function hslToHex(h,s,l){h/=360;s/=100;l/=100;let r,g,b;if(s===0){r=g=b=l;}else{const hue2rgb=(p,q,t)=>{if(t<0)t+=1;if(t>1)t-=1;if(t<1/6)return p+(q-p)*6*t;if(t<1/2)return q;if(t<2/3)return p+(q-p)*(2/3-t)*6;return p;};const q=l<0.5?l*(1+s):l+s-l*s,p=2*l-q;r=hue2rgb(p,q,h+1/3);g=hue2rgb(p,q,h);b=hue2rgb(p,q,h-1/3);}return '#'+[r,g,b].map(x=>Math.round(x*255).toString(16).padStart(2,'0')).join('');}
function generate(){const base=document.getElementById('baseColor').value;const scheme=document.getElementById('scheme').value;const[h,s,l]=hexToHsl(base);let colors=[];
if(scheme==='complementary')colors=[base,hslToHex((h+180)%360,s,l),hslToHex((h+150)%360,s,l),hslToHex((h+210)%360,s,l),hslToHex(h,s,Math.min(l+20,95))];
else if(scheme==='analogous')colors=[hslToHex((h-30+360)%360,s,l),hslToHex((h-15+360)%360,s,l),base,hslToHex((h+15)%360,s,l),hslToHex((h+30)%360,s,l)];
else if(scheme==='triadic')colors=[base,hslToHex((h+120)%360,s,l),hslToHex((h+240)%360,s,l),hslToHex(h,s,Math.max(l-15,5)),hslToHex(h,s,Math.min(l+15,95))];
else colors=[hslToHex(h,s,Math.max(l-30,5)),hslToHex(h,s,Math.max(l-15,5)),base,hslToHex(h,s,Math.min(l+15,95)),hslToHex(h,s,Math.min(l+30,95))];
const pal=document.getElementById('palette');pal.textContent = '';const vals=document.getElementById('values');vals.textContent = '';
colors.forEach(c=>{const d=document.createElement('div');d.style.cssText='flex:1;background:'+c+';cursor:pointer;transition:flex 0.2s;';d.title='Click to copy '+c;d.onmouseenter=()=>d.style.flex='1.5';d.onmouseleave=()=>d.style.flex='1';d.onclick=()=>navigator.clipboard.writeText(c).then(()=>{d.style.outline='3px solid white';setTimeout(()=>d.style.outline='none',800);});pal.appendChild(d);
vals.innerHTML+='<span style="color:'+c+';cursor:pointer;margin-right:6px;" onclick="navigator.clipboard.writeText(\''+c+'\')">'+c+'</span>';});}
document.getElementById('baseColor').oninput=generate;document.getElementById('scheme').onchange=generate;document.getElementById('genBtn').onclick=()=>{document.getElementById('baseColor').value='#'+Math.floor(Math.random()*16777215).toString(16).padStart(6,'0');generate();};generate();
