
document.addEventListener("DOMContentLoaded", () => {
    const paywallHTML = `
        <div id="ma-pro-container" style="
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
            border-top: 1px solid #e2e8f0;
            padding: 12px 16px;
            box-shadow: 0 -4px 12px rgba(0,0,0,0.03);
            font-family: 'Inter', -apple-system, sans-serif;
            z-index: 99999;
            box-sizing: border-box;
            transition: all 0.3s ease;
            text-align: center;
        ">
            <div id="ma-pro-default">
                <p style="margin: 0 0 8px 0; font-size: 13px; color: #475569; font-weight: 500;">Take your productivity to the next level.</p>
                <div style="display: flex; gap: 8px; justify-content: center;">
                    <button id="ma-btn-upgrade" style="
                        background: #635bff; color: #fff; border: none; padding: 8px 14px;
                        border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer;
                        box-shadow: 0 2px 4px rgba(99, 91, 255, 0.3); transition: transform 0.1s;
                    ">💎 Get PRO Access</button>
                    <button id="ma-btn-license" style="
                        background: #fff; color: #475569; border: 1px solid #cbd5e1; padding: 8px 14px;
                        border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer;
                        transition: background 0.1s;
                    ">Enter Key</button>
                </div>
            </div>
            
            <div id="ma-pro-input" style="display: none;">
                <p style="margin: 0 0 8px 0; font-size: 12px; color: #475569;">Enter your 16-character license key:</p>
                <div style="display: flex; gap: 8px; justify-content: center;">
                    <input type="text" id="ma-key-input" placeholder="A1B2-C3D4-E5F6-G7H8" style="
                        border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px; font-family: monospace;
                        font-size: 13px; width: 180px; outline: none; text-transform: uppercase;
                    "/>
                    <button id="ma-btn-verify" style="
                        background: #10b981; color: #fff; border: none; padding: 6px 14px;
                        border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer;
                    ">Verify</button>
                </div>
                <p id="ma-license-error" style="margin: 6px 0 0 0; color: #ef4444; font-size: 11px; display: none;"></p>
                <a href="#" id="ma-btn-back" style="display: inline-block; margin-top: 6px; font-size: 11px; color: #64748b; text-decoration: none;">← Back</a>
            </div>
            
            <div id="ma-pro-success" style="display: none; align-items: center; justify-content: center; color: #10b981; font-weight: 600; font-size: 14px;">
                <svg style="width:18px;height:18px;margin-right:6px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                PRO Features Unlocked
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', paywallHTML);
    // Add padding to body so the fixed footer doesn't overlap extension content
    document.body.style.paddingBottom = '90px';

    const defaultView = document.getElementById("ma-pro-default");
    const inputView = document.getElementById("ma-pro-input");
    const successView = document.getElementById("ma-pro-success");
    const errorMsg = document.getElementById("ma-license-error");

    const btnUpgrade = document.getElementById("ma-btn-upgrade");
    const btnLicense = document.getElementById("ma-btn-license");
    const btnVerify = document.getElementById("ma-btn-verify");
    const btnBack = document.getElementById("ma-btn-back");
    const keyInput = document.getElementById("ma-key-input");

    // Check existing license
    chrome.storage.local.get(["omnisuite_pro_key_network-monitor-pro"], (res) => {
        if (res["omnisuite_pro_key_network-monitor-pro"]) {
            unlockPro();
        }
    });

    let pollInterval = null;
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    btnUpgrade.addEventListener("click", () => {
        const uuid = generateUUID();
        window.open("https://buy.stripe.com/aFa8wP5meazp1zv5FY0ZW1q?client_reference_id=" + uuid, "_blank");
        
        if (!pollInterval) {
            btnUpgrade.innerText = "⏳ Awaiting Payment...";
            let pollCount = 0;
            pollInterval = setInterval(async () => {
                pollCount++;
                if (pollCount > 100) { // Stop after ~5 minutes
                    clearInterval(pollInterval);
                    pollInterval = null;
                    btnUpgrade.innerText = "💎 Get PRO Access";
                    return;
                }
                try {
                    const res = await fetch(`https://microassets-license-server-production.up.railway.app/poll?uuid=${uuid}`);
                    const data = await res.json();
                    if (data.ready && data.key) {
                        clearInterval(pollInterval);
                        keyInput.value = data.key;
                        btnVerify.click();
                        btnUpgrade.innerText = "💎 Get PRO Access";
                    }
                } catch (e) { console.error("Caught error:", e); }
            }, 3000);
        }
    });

    btnLicense.addEventListener("click", () => {
        defaultView.style.display = "none";
        inputView.style.display = "block";
    });

    btnBack.addEventListener("click", (e) => {
        e.preventDefault();
        inputView.style.display = "none";
        defaultView.style.display = "block";
        errorMsg.style.display = "none";
    });

    btnVerify.addEventListener("click", async () => {
        const key = keyInput.value.trim().toUpperCase();
        if (key.length < 8) {
            showError("Invalid key format.");
            return;
        }
        
        btnVerify.innerText = "Verifying...";
        try {
            const res = await fetch(`https://microassets-license-server-production.up.railway.app/validate?key=${encodeURIComponent(key)}`);
            const data = await res.json();
            
            if (data.valid && (data.product === "network-monitor-pro" || data.product === "omnisuite-master-suite")) {
                let obj = {};
                obj["omnisuite_pro_key_network-monitor-pro"] = key;
                chrome.storage.local.set(obj, () => {
                    unlockPro();
                });
            } else {
                showError("Invalid or expired license key.");
            }
        } catch (e) {
            showError("Connection error. Try again.");
        }
        btnVerify.innerText = "Verify";
    });

    function showError(msg) {
        errorMsg.innerText = msg;
        errorMsg.style.display = "block";
    }

    function unlockPro() {
        defaultView.style.display = "none";
        inputView.style.display = "none";
        successView.style.display = "flex";
        document.body.classList.add("ma-pro-active");
    }
});
