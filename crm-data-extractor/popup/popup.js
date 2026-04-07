document.addEventListener('DOMContentLoaded', async () => {
    const scanBtn = document.getElementById('scanBtn');
    const exportBtn = document.getElementById('exportCsvBtn');
    const resultsPanel = document.getElementById('resultsPanel');
    const upsellPanel = document.getElementById('upsellPanel');
    const rowCount = document.getElementById('rowCount');
    const colCount = document.getElementById('colCount');
    const creditsBadge = document.getElementById('creditsBadge');
    
    let extractedData = null;

    // Load credits from generic sync storage
    const { credits = 5 } = await chrome.storage.sync.get('credits');
    creditsBadge.textContent = `${credits} Left`;
    
    if (credits <= 0) {
        scanBtn.disabled = true;
        scanBtn.style.opacity = '0.5';
        upsellPanel.classList.remove('hidden');
    }

    // Attempt to identify the CRM based on URL
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const url = tabs[0].url;
        const pageTitle = document.getElementById('pageContext');
        if (url.includes('salesforce.com')) pageTitle.textContent = "Salesforce Detected";
        else if (url.includes('hubspot.com')) pageTitle.textContent = "HubSpot Detected";
        else if (url.includes('linkedin.com')) pageTitle.textContent = "LinkedIn Detected";
        else pageTitle.textContent = "Generic Table Detected";
    });

    scanBtn.addEventListener('click', async () => {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        scanBtn.querySelector('.btn-text').textContent = "Scanning Virtual DOM...";
        
        // Inject content script into active tab
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['content.js']
        }, () => {
            // After script injection, ask it to extract
            chrome.tabs.sendMessage(tab.id, { action: "EXTRACT_DATA" }, (response) => {
                scanBtn.querySelector('.btn-text').textContent = "Scan Page for Data";
                
                if (response && response.data && response.data.length > 0) {
                    extractedData = response.data;
                    rowCount.textContent = extractedData.length;
                    colCount.textContent = extractedData[0] ? Object.keys(extractedData[0]).length : 0;
                    
                    resultsPanel.classList.remove('hidden');
                    scanBtn.style.display = 'none';
                    document.getElementById('tableStatus').textContent = "Data ready for export.";
                    
                    // Deduct credit
                    chrome.storage.sync.set({ credits: credits - 1 });
                    creditsBadge.textContent = `${credits - 1} Left`;
                } else {
                    document.getElementById('tableStatus').textContent = "Failed to find any readable table rows.";
                    document.getElementById('tableStatus').style.color = "#ef4444";
                }
            });
        });
    });

    exportBtn.addEventListener('click', () => {
        if (!extractedData) return;
        
        // Convert JSON to CSV
        const headers = Object.keys(extractedData[0]);
        const csvRows = [headers.join(',')];
        
        for (const row of extractedData) {
            const values = headers.map(header => {
                const escaped = ('' + row[header]).replace(/"/g, '""');
                return `"${escaped}"`;
            });
            csvRows.push(values.join(','));
        }
        
        const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `crm_export_${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    });
});
