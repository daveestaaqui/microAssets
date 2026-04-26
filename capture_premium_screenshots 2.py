import os
import glob
import json
import base64
import time
from PIL import Image
from playwright.sync_api import sync_playwright

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
OUT_DIR = os.path.join(BASE_DIR, "new_promo_screenshots")

os.makedirs(OUT_DIR, exist_ok=True)

def get_dominant_color(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((50, 50))
        colors = img.getcolors(2500)
        colors.sort(key=lambda x: x[0], reverse=True)
        for count, color in colors:
            r, g, b = color
            # ignore pure whites and blacks
            if r > 240 and g > 240 and b > 240:
                continue
            if r < 20 and g < 20 and b < 20:
                continue
            # avoid greys
            if abs(r-g) < 15 and abs(g-b) < 15:
                continue
            return f"{r}, {g}, {b}"
        return "100, 100, 255"
    except Exception as e:
        return "100, 100, 255"

def build_html_template(name, desc, color_rgb, popup_url, original_icon_url):
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                width: 1280px;
                height: 800px;
                background: linear-gradient(135deg, #fcfbf9 0%, #f4f1eb 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }}
            /* Ambient background glow */
            .glow {{
                position: absolute;
                width: 1000px;
                height: 1000px;
                background: radial-gradient(circle, rgba({color_rgb}, 0.15) 0%, transparent 70%);
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 0;
                filter: blur(80px);
            }}
            /* The actual popup iframe */
            iframe {{
                position: relative;
                z-index: 10;
                border: 1px solid rgba(0,0,0,0.05);
                box-shadow: 0 30px 80px rgba(0,0,0,0.1), 0 0 0 1px rgba(0,0,0,0.02), 0 0 140px rgba({color_rgb}, 0.15);
                border-radius: 12px;
                width: 320px; 
                height: 500px;
                background: #ffffff;
                transform: scale(1.3);
            }}
        </style>
    </head>
    <body>
        <div class="glow"></div>
        <!-- The iframe loads the real extension locally -->
        <iframe id="extension-frame" src="{popup_url}"></iframe>
    </body>
    </html>
    """
    return html

def run():
    folders = sorted([f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f)) and os.path.exists(os.path.join(BASE_DIR, f, "manifest.json"))])
    print(f"Found {len(folders)} extension folders.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-web-security'])
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        
        # We will mock the chrome storage API to avoid extensions failing on load
        mock_script = """
            window.chrome = window.chrome || {};
            window.chrome.runtime = { id: 'mock_test_id' };
            window.chrome.storage = {
                local: {
                    get: (keys, cb) => { if(cb) cb({}); return Promise.resolve({}); },
                    set: (obj, cb) => { if (cb) cb(); return Promise.resolve(); }
                },
                sync: {
                    get: (keys, cb) => { if(cb) cb({}); return Promise.resolve({}); },
                    set: (obj, cb) => { if (cb) cb(); return Promise.resolve(); }
                }
            };
            window.browser = window.chrome;
        """
        
        # Process all extensions
        test_folders = folders

        
        for folder in test_folders:
            if folder.endswith("-firefox"): continue
                
            manifest_path = os.path.join(BASE_DIR, folder, "manifest.json")
            popup_path = os.path.join(BASE_DIR, folder, "popup", "index.html")
            
            if not os.path.exists(popup_path):
                continue
                
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                name = manifest.get("name", folder)
                desc = manifest.get("description", "")
                
                # Check for logo
                icon_full_path = ""
                # Try manifest defined icons
                if "icons" in manifest and "128" in manifest["icons"]:
                    p = os.path.join(BASE_DIR, folder, manifest["icons"]["128"])
                    if os.path.exists(p): icon_full_path = p
                
                # Fallbacks
                if not icon_full_path:
                    for fallback in ["icon128.png", "popup/icon.png", "icons/icon128.png", "icons/icon48.png"]:
                        p = os.path.join(BASE_DIR, folder, fallback)
                        if os.path.exists(p):
                            icon_full_path = p
                            break
                    
                if icon_full_path:
                    color_rgb = get_dominant_color(icon_full_path)
                    with open(icon_full_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                        icon_data_url = f"data:image/png;base64,{encoded_string}"
                else:
                    color_rgb = "100, 100, 100"
                    icon_data_url = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMCIgaGVpZ2h0PSIxMCI+PHJlY3Qgd2lkdGg9IjEwIiBoZWlnaHQ9IjEwIiBmaWxsPSIjY2NjIi8+PC9zdmc+"
                
                popup_file_url = f"file://{popup_path}"
                html = build_html_template(name, desc, color_rgb, popup_file_url, icon_data_url)
                
                # Write temp html
                temp_html_path = os.path.join(BASE_DIR, "temp_promo.html")
                with open(temp_html_path, "w") as f:
                    f.write(html)
                    
                page = context.new_page()
                page.add_init_script(mock_script)
                
                # Wait until network idle so images within the iframe load
                page.goto(f"file://{temp_html_path}", wait_until="networkidle")
                
                # Inject the mock script DIRECTLY into the iframe instance as well
                frame = page.frames[1] if len(page.frames) > 1 else None
                if frame:
                    # Give it a bit of time to execute internal JS and render
                    time.sleep(1.0)
                    # We can attempt to fix iframe size to match content
                    try:
                        w = frame.evaluate("document.body.scrollWidth")
                        h = frame.evaluate("document.body.scrollHeight")
                        # adjust iframe size in container
                        page.evaluate(f"document.getElementById('extension-frame').style.width = '{min(w, 400)}px';")
                        page.evaluate(f"document.getElementById('extension-frame').style.height = '{min(h, 550)}px';")
                        time.sleep(0.5)
                    except:
                        pass
                else:
                    time.sleep(1.5)
                    
                out_png = os.path.join(OUT_DIR, f"{folder}.png")
                page.screenshot(path=out_png)
                print(f"Captured {folder} (Color: {color_rgb})")
                
                page.close()
            except Exception as e:
                print(f"Error processing {folder}: {e}")
                
        browser.close()
        
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)

if __name__ == "__main__":
    run()
