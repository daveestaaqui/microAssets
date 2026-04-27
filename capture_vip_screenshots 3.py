import os
import glob
import json
import base64
import time
import sys
from PIL import Image
from playwright.sync_api import sync_playwright

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
OUT_DIR = os.path.join(BASE_DIR, "new_promo_screenshots")

os.makedirs(OUT_DIR, exist_ok=True)

def get_dominant_color(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((100, 100))
        pixels = list(img.getdata())
        
        # ignore light pixels (like cream background)
        filtered_pixels = [p for p in pixels if (p[0]*0.299 + p[1]*0.587 + p[2]*0.114) <= 200]
        
        if not filtered_pixels:
             return "100, 100, 100"
             
        from collections import Counter
        counter = Counter(filtered_pixels)
        most_common = counter.most_common(20)
        
        unique_colors = []
        for color, count in most_common:
            if not unique_colors:
                unique_colors.append(color)
            else:
                is_unique = True
                for uc in unique_colors:
                    dist = sum((c1 - c2) ** 2 for c1, c2 in zip(color, uc))
                    if dist < 1000:
                        is_unique = False
                        break
                if is_unique:
                    unique_colors.append(color)
            if len(unique_colors) == 2:
                break
        
        if not unique_colors:
             return "100, 100, 100"
             
        # Use the accent color instead of darkest color for glow (often second color)
        accent = unique_colors[1] if len(unique_colors) > 1 else unique_colors[0]
        return f"{accent[0]}, {accent[1]}, {accent[2]}"
    except Exception as e:
        return "100, 100, 100"

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
                background: radial-gradient(circle, rgba({color_rgb}, 0.18) 0%, transparent 70%);
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
                border-radius: 20px; /* Enhanced for boutique style */
                width: 320px; 
                height: 500px;
                background: #ffffff; /* Fallback for transparency */
                transform: scale(1.3);
            }}
        </style>
    </head>
    <body>
        <div class="glow"></div>
        <iframe id="extension-frame" src="{popup_url}"></iframe>
    </body>
    </html>
    """
    return html

def run():
    target_folders = sys.argv[1:] if len(sys.argv) > 1 else [
        "timestamp-converter", "link-checker", "color-palette-generator", "privacy-scanner"
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-web-security'])
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        
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
        
        for folder in target_folders:
            manifest_path = os.path.join(BASE_DIR, folder, "manifest.json")
            popup_path = os.path.join(BASE_DIR, folder, "popup", "index.html")
            
            custom_popup = False
            if not os.path.exists(popup_path):
                # Fallback to a simple layout with just the icon if no popup HTML
                custom_popup = True
                popup_path = os.path.join(BASE_DIR, "dummy_popup.html")
                icon_path_for_html = os.path.join(BASE_DIR, folder, "icons", "icon.png")
                with open(popup_path, "w") as dp:
                    dp.write(f"<html><body style='display:flex;align-items:center;justify-content:center;height:100%;background:#F8F5EE;margin:0;'><img src='file://{icon_path_for_html}' style='width:128px;height:128px;'></body></html>")
                
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            name = manifest.get("name", folder)
            desc = manifest.get("description", "")
            
            icon_full_path = ""
            for fallback in ["icon128.png", "popup/icon.png", "icons/icon128.png", "icons/icon-128.png"]:
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
            
            # Use specific known colors for the glow instead of dynamic fallback to guarantee matching the boutique css mapping
            glow_override = {
                "timestamp-converter": "184, 83, 56", # Terracotta
                "link-checker": "43, 60, 79",         # Navy
                "color-palette-generator": "201, 156, 59", # Mustard
                "privacy-scanner": "77, 54, 74",      # Plum
                "cookie-manager": "177, 126, 81",
                "css-inspector-pro": "63, 72, 40",
                "json-formatter": "199, 113, 88",
                "screenshot-capture": "193, 191, 197",
                "qr-code-generator": "129, 122, 67",
                "regex-tester": "93, 119, 105",
                "markdown-preview": "183, 190, 182",
                "word-counter": "182, 173, 158",
                "time-tracker": "171, 78, 37",
                "url-encoder-decoder": "47, 98, 98"
            }
            if folder in glow_override:
                color_rgb = glow_override[folder]
                
            html = build_html_template(name, desc, color_rgb, popup_file_url, icon_data_url)
            
            temp_html_path = os.path.join(BASE_DIR, "temp_promo_vip.html")
            with open(temp_html_path, "w") as f:
                f.write(html)
                
            page = context.new_page()
            page.add_init_script(mock_script)
            
            page.goto(f"file://{temp_html_path}", wait_until="networkidle")
            
            frame = page.frames[1] if len(page.frames) > 1 else None
            if frame:
                time.sleep(1.0)
                try:
                    w = frame.evaluate("document.body.scrollWidth")
                    h = frame.evaluate("document.body.scrollHeight")
                    page.evaluate(f"document.getElementById('extension-frame').style.width = '{min(w, 400)}px';")
                    page.evaluate(f"document.getElementById('extension-frame').style.height = '{min(h, 550)}px';")
                    time.sleep(0.5)
                except:
                    pass
            else:
                time.sleep(1.5)
                
            out_png = os.path.join(OUT_DIR, f"{folder}.png")
            page.screenshot(path=out_png)
            print(f"Captured FLAGSHIP {folder} (Color: {color_rgb})")
            page.close()
            
        browser.close()
        
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)

if __name__ == "__main__":
    run()
