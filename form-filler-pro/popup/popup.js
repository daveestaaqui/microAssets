
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'smart_form_filler_pro';
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

const profileFields=['firstName','lastName','email','phone','company','address','city','state','zip','country'];
const defaultProfile={name:'Default',firstName:'',lastName:'',email:'',phone:'',company:'',address:'',city:'',state:'',zip:'',country:'US'};
function load(){chrome.storage.local.get(['formProfiles'],d=>{const p=d.formProfiles||[defaultProfile];const sel=document.getElementById('profiles');sel.textContent = '';p.forEach((pr,i)=>{const o=document.createElement('option');o.value=i;o.textContent=pr.name;sel.appendChild(o);});showFields(0);if(!d.formProfiles)chrome.storage.local.set({formProfiles:[defaultProfile]});});}
function showFields(i){chrome.storage.local.get(['formProfiles'],d=>{const p=(d.formProfiles||[defaultProfile])[i];const el=document.getElementById('fields');el.innerHTML=profileFields.map(f=>`<div class="field"><label>${f}</label><input type="text" data-field="${f}" value="${p[f]||''}"></div>`).join('');});}
document.getElementById('profiles').onchange=e=>showFields(parseInt(e.target.value));
document.getElementById('saveBtn').onclick=()=>{const i=parseInt(document.getElementById('profiles').value);const inputs=document.querySelectorAll('#fields input');chrome.storage.local.get(['formProfiles'],d=>{const p=d.formProfiles||[defaultProfile];inputs.forEach(inp=>{p[i][inp.dataset.field]=inp.value;});chrome.storage.local.set({formProfiles:p});});};
document.getElementById('newBtn').onclick=()=>{chrome.storage.local.get(['formProfiles','omnisuite_pro_key_form-filler-pro'],d=>{const p=d.formProfiles||[defaultProfile];if(p.length>=1&&!d['omnisuite_pro_key_form-filler-pro']){document.getElementById('gate').style.display='block';return;}p.push({...defaultProfile,name:'Profile '+(p.length+1)});chrome.storage.local.set({formProfiles:p},load);});};
document.getElementById('fillBtn').onclick=()=>{const i=parseInt(document.getElementById('profiles').value);chrome.storage.local.get(['formProfiles'],d=>{const p=(d.formProfiles||[defaultProfile])[i];chrome.tabs.query({active:true,currentWindow:true},tabs=>{chrome.scripting.executeScript({target:{tabId:tabs[0].id},args:[p],func:(profile)=>{const map={firstName:['first','fname','given'],lastName:['last','lname','surname','family'],email:['email','mail'],phone:['phone','tel','mobile'],company:['company','org','business'],address:['address','street','addr'],city:['city','town'],state:['state','region','province'],zip:['zip','postal','postcode'],country:['country']};
document.querySelectorAll('input,select,textarea').forEach(el=>{const n=(el.name+' '+el.id+' '+(el.placeholder||'')+' '+(el.labels?.[0]?.textContent||'')).toLowerCase();for(const[field,keywords]of Object.entries(map)){if(keywords.some(k=>n.includes(k))&&profile[field]){if(el.tagName==='SELECT'){Array.from(el.options).forEach(o=>{if(o.value.toLowerCase()===profile[field].toLowerCase()||o.text.toLowerCase()===profile[field].toLowerCase())el.value=o.value;});}else{el.value=profile[field];el.dispatchEvent(new Event('input',{bubbles:true}));}break;}}});}});});});};load();
