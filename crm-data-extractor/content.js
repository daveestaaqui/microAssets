// Listen for extraction requests from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "EXTRACT_DATA") {
        const data = injectScraperHalt();
        sendResponse({ status: "success", data: data });
    }
    return true; // Keep message channel open for async
});

// Primary parsing engine
function injectScraperHalt() {
    let rows = [];
    const url = window.location.href;

    try {
        if (url.includes('salesforce.com')) {
            rows = scrapeSalesforceLightning();
        } else if (url.includes('hubspot.com')) {
            rows = scrapeHubSpot();
        } else if (url.includes('linkedin.com')) {
            rows = scrapeLinkedIn();
        } else {
            rows = scrapeGenericTable();
        }
    } catch (e) {
        console.error("CRM Extractor Error:", e);
    }
    
    return rows;
}

// 1. Salesforce Lightning DataGrid
function scrapeSalesforceLightning() {
    const data = [];
    // Salesforce wraps table rows in tr elements with class 'slds-hint-parent' or inside UI virtualization
    const rows = document.querySelectorAll('tr.slds-hint-parent, table.slds-table tbody tr');
    
    if (rows.length === 0) return scrapeGenericTable(); // Fallback
    
    // Get headers
    const headerNodes = document.querySelectorAll('th span.slds-truncate, th a.toggle');
    const headers = Array.from(headerNodes).map(th => th.textContent.trim() || 'Column').slice(0, 15);
    
    rows.forEach((row, i) => {
        const cells = Array.from(row.querySelectorAll('td, th')).slice(0, 15);
        if (cells.length > 0) {
            const rowData = {};
            cells.forEach((cell, idx) => {
                const head = headers[idx] || `Column_${idx+1}`;
                rowData[head] = cell.innerText.trim() || cell.textContent.trim();
            });
            data.push(rowData);
        }
    });
    return data;
}

// 2. HubSpot CRM Table
function scrapeHubSpot() {
    const data = [];
    // HubSpot uses virtualized div rows for contacts
    const rows = document.querySelectorAll('tr.ui-table__row, div[role="row"]');
    
    if (rows.length === 0) return scrapeGenericTable();
    
    // Attempt Header Extraction
    const headerNodes = document.querySelectorAll('th span.ThWrapper__HeaderText, div[role="columnheader"]');
    const headers = Array.from(headerNodes).map(th => th.innerText.trim()).filter(h => h.length > 0);
    
    rows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td, div[role="cell"]'));
        if (cells.length > 0) {
            const rowData = {};
            cells.forEach((cell, idx) => {
                const head = headers[idx] || `Column_${idx+1}`;
                rowData[head] = cell.innerText.trim().replace(/\n/g, ' ');
            });
            data.push(rowData);
        }
    });
    return data;
}

// 3. LinkedIn Recruiter/Search Extractor
function scrapeLinkedIn() {
    const data = [];
    // Scrape candidate profile blocks
    const cards = document.querySelectorAll('.reusable-search__result-container, .artdeco-list__item');
    
    if (cards.length === 0) return scrapeGenericTable();
    
    cards.forEach(card => {
        const nameNode = card.querySelector('.app-aware-link span[aria-hidden="true"], .entity-result__title');
        const titleNode = card.querySelector('.entity-result__primary-subtitle');
        const locNode = card.querySelector('.entity-result__secondary-subtitle');
        const urlNode = card.querySelector('a.app-aware-link');
        
        data.push({
            "Name": nameNode ? nameNode.innerText.trim() : 'Unknown',
            "Headline": titleNode ? titleNode.innerText.trim() : '',
            "Location": locNode ? locNode.innerText.trim() : '',
            "URL": urlNode ? urlNode.href : ''
        });
    });
    return data;
}

// 4. Ultimate Fallback: Scrape the largest HTML table on the page
function scrapeGenericTable() {
    const data = [];
    const tables = Array.from(document.querySelectorAll('table'));
    
    if (tables.length === 0) {
        // Look for CSS Grid or Flex grids
        return attemptDivGridScrape();
    }
    
    // Find the largest table
    tables.sort((a, b) => b.querySelectorAll('tr').length - a.querySelectorAll('tr').length);
    const table = tables[0];
    
    const rows = Array.from(table.querySelectorAll('tr'));
    
    // Extract headers from first row
    const headerCells = rows[0].querySelectorAll('th, td');
    const headers = Array.from(headerCells).map((c, i) => c.innerText.trim() || `Col_${i}`);
    
    for (let i = 1; i < rows.length; i++) {
        const cells = Array.from(rows[i].querySelectorAll('td'));
        if (cells.length > 0) {
            const rowData = {};
            cells.forEach((cell, idx) => {
                const head = headers[idx] || `Col_${idx}`;
                rowData[head] = cell.innerText.trim();
            });
            data.push(rowData);
        }
    }
    return data;
}

function attemptDivGridScrape() {
    // If no tables exist, we look for highly repeated div structures (virtual lists)
    // Extremely experimental AST-style DOM parsing.
    return [{"Warning": "No clean data table detected."}];
}
