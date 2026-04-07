// Invoice Data Extractor — parses invoice tables and line items
(function() {
  'use strict';

  function extractInvoiceData() {
    const rows = [];

    // Strategy 1: Look for HTML tables
    document.querySelectorAll('table').forEach(table => {
      const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
      table.querySelectorAll('tr').forEach(tr => {
        const cells = Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim());
        if (cells.length > 1) rows.push(cells);
      });
    });

    // Strategy 2: Look for common invoice meta
    const datePat = /\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}/g;
    const moneyPat = /[$€£]\s?\d+([,.]\d+)*/g;
    const bodyText = document.body.innerText;
    const dates  = bodyText.match(datePat) || [];
    const amounts = bodyText.match(moneyPat) || [];

    return { rows, dates, amounts, url: location.href, title: document.title };
  }

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type === 'EXTRACT_INVOICE') {
      sendResponse(extractInvoiceData());
    }
  });
})();
