
// === OmniSuite Self-Healing System ===
(function() {
  const _api = (typeof browser !== 'undefined' && browser.storage) ? browser : chrome;
  const EXT_ID = 'page_ruler_and_measure';
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

document.getElementById('startBtn').onclick=function(){
chrome.tabs.query({active:true,currentWindow:true},function(tabs){
chrome.scripting.executeScript({target:{tabId:tabs[0].id},func:function(){
if(document.getElementById('flowkit-ruler'))return;
var overlay=document.createElement('div');overlay.id='flowkit-ruler';
overlay.style.cssText='position:fixed;top:0;left:0;pointer-events:none;z-index:999999;';
var label=document.createElement('div');
label.style.cssText='position:fixed;padding:4px 8px;background:#a855f7;color:white;font-size:11px;font-family:system-ui;border-radius:4px;z-index:999999;pointer-events:none;display:none;';
document.body.appendChild(overlay);document.body.appendChild(label);
document.addEventListener('mousemove',function(e){
var el=document.elementFromPoint(e.clientX,e.clientY);if(!el)return;
if(overlay.firstChild)overlay.firstChild.remove();
var r=el.getBoundingClientRect();
var box=document.createElement('div');
box.style.cssText='position:fixed;left:'+r.left+'px;top:'+r.top+'px;width:'+r.width+'px;height:'+r.height+'px;border:2px solid #a855f7;background:rgba(168,85,247,0.1);';
overlay.appendChild(box);label.style.display='block';
label.style.left=(e.clientX+12)+'px';label.style.top=(e.clientY+12)+'px';
label.textContent=Math.round(r.width)+'x'+Math.round(r.height)+'px';});
document.addEventListener('click',function(e){
var el=document.elementFromPoint(e.clientX,e.clientY);if(el){
var r=el.getBoundingClientRect();
navigator.clipboard.writeText('W:'+Math.round(r.width)+' H:'+Math.round(r.height)+' X:'+Math.round(r.left)+' Y:'+Math.round(r.top));}});}});window.close();});};
