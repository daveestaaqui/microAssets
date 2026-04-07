// JSON Formatter — detects raw JSON pages and renders them with syntax highlighting
(function() {
  'use strict';
  const KEY = 'json_formatter_enabled';

  function isJsonPage() {
    const ct = document.contentType || '';
    if (ct.includes('json')) return true;
    const pre = document.querySelector('body > pre:only-child');
    if (pre && (pre.textContent.trim().startsWith('{') || pre.textContent.trim().startsWith('['))) return true;
    return false;
  }

  function colorize(json) {
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      match => {
        let cls = 'json-number';
        if (/^"/.test(match)) cls = /:$/.test(match) ? 'json-key' : 'json-string';
        else if (/true|false/.test(match)) cls = 'json-bool';
        else if (/null/.test(match)) cls = 'json-null';
        return `<span class="${cls}">${match}</span>`;
      });
  }

  browser.storage.local.get([KEY], r => {
    if (r[KEY] === false) return;
    if (!isJsonPage()) return;

    const raw = document.body.innerText.trim();
    let parsed;
    try { parsed = JSON.parse(raw); } catch(e) { return; }

    const pretty = JSON.stringify(parsed, null, 2);
    const style = `
      <style>
        body { background:#0d1117; color:#c9d1d9; font-family:monospace; font-size:13px; padding:20px; }
        .json-key { color:#79c0ff; } .json-string { color:#a5d6ff; }
        .json-number { color:#f2cc60; } .json-bool { color:#ff7b72; }
        .json-null { color:#8b949e; }
      </style>`;
    document.open();
    document.write(`<!DOCTYPE html><html><head>${style}</head><body><pre>${colorize(pretty)}</pre></body></html>`);
    document.close();
  });
})();
