const requests=[];
chrome.webRequest.onCompleted.addListener(d=>{requests.push({url:d.url,method:d.method||'GET',status:d.statusCode,type:d.type,ts:d.timeStamp,tabId:d.tabId,size:d.responseHeaders?.find(h=>h.name.toLowerCase()==='content-length')?.value||0});if(requests.length>500)requests.shift();},{urls:["<all_urls>"]},["responseHeaders"]);
chrome.runtime.onMessage.addListener((msg,sender,sendResponse)=>{if(msg.type==='getRequests'){const tabId=msg.tabId;sendResponse(requests.filter(r=>r.tabId===tabId).slice(-100));}return true;});
