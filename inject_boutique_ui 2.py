import os
import re
from collections import Counter
from PIL import Image

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"

def get_dominant_colors(image_path, num_colors=2, exclude_hex="#F8F5EE"):
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return ["#2E2522", "#2B3C4F"] # Fallback

    img = img.resize((100, 100))
    pixels = list(img.getdata())
    
    def is_light(c): return (c[0]*0.299 + c[1]*0.587 + c[2]*0.114) > 200
    
    filtered_pixels = [p for p in pixels if not is_light(p)]

    if not filtered_pixels:
        return ["#2E2522", "#2B3C4F"] # Fallback

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
        if len(unique_colors) == num_colors:
            break
            
    while len(unique_colors) < num_colors:
        unique_colors.append(unique_colors[0] if unique_colors else (46, 37, 34))

    def luminance(c): return 0.299*c[0] + 0.587*c[1] + 0.114*c[2]
    
    unique_colors.sort(key=luminance) # Darkest first
    dark_c = unique_colors[0]
    accent_c = unique_colors[1]
    
    # Enforce dark text rule for legibility (lum < 100)
    if luminance(dark_c) > 100:
        factor = 80 / luminance(dark_c)
        dark_c = (int(dark_c[0] * factor), int(dark_c[1] * factor), int(dark_c[2] * factor))
        
    dark_hex = f"#{dark_c[0]:02x}{dark_c[1]:02x}{dark_c[2]:02x}"
    accent_hex = f"#{accent_c[0]:02x}{accent_c[1]:02x}{accent_c[2]:02x}"
    
    return dark_hex, accent_hex

精品_css_template = """
/* 🎨 BEPOKE BOUTIQUE UI OVERRIDE */
:root {{
    --app-canvas: {canvas};
    --app-dark: {dark};
    --app-accent: {accent};
}}

/* Eradicate the old Solid AI Slop */
body {{
    background-color: var(--app-canvas) !important;
    background-image: none !important;
    color: var(--app-dark) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif !important;
    letter-spacing: -0.01em !important;
    width: 320px;
}}

/* Organic header - floaty, elegant typography */
.sdal-header {{
    background: transparent !important;
    box-shadow: none !important;
    border-bottom: 0px !important;
    padding: 24px 24px 12px 24px !important;
    margin-bottom: 0px !important;
    justify-content: center !important;
}}
.sdal-logo {{
    display: flex !important;
    align-items: center !important;
}}
.sdal-logo span {{
    font-family: "Playfair Display", "Georgia", serif !important;
    font-weight: 600 !important;
    font-size: 20px !important;
    color: var(--app-dark) !important;
    letter-spacing: 0.02em !important;
    margin-left: 8px !important;
}}
.sdal-img {{
    width: 44px !important;
    height: 44px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
}}

/* Clean, organic form body */
.sdal-body {{
    padding: 12px 24px 24px 24px !important;
    border-radius: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 16px !important;
}}

/* Text styling */
h1, h2, h3, h4 {{
    color: var(--app-dark) !important;
    font-family: "Playfair Display", "Georgia", serif !important;
}}

/* High-contrast, tailored inputs */
input, textarea, select {{
    background: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    color: var(--app-dark) !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    box-sizing: border-box !important;
    width: 100% !important;
}}
input:focus, textarea:focus, select:focus {{
    border-color: var(--app-accent) !important;
    box-shadow: 0 0 0 3px rgba(0,0,0,0.05) !important;
    outline: none !important;
}}

/* Elegant action buttons */
button, .sdal-btn {{
    background: var(--app-accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 12px 18px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    transition: transform 0.2s ease, filter 0.2s ease !important;
    letter-spacing: 0.02em !important;
    cursor: pointer !important;
    width: 100% !important;
    text-align: center !important;
    box-sizing: border-box !important;
}}
button:hover, .sdal-btn:hover {{
    filter: brightness(1.1) !important;
    transform: translateY(-1px) !important;
}}
button:active, .sdal-btn:active {{
    transform: translateY(1px) !important;
}}

/* Checkboxes & Labels adjusted for organic flow */
.option-row, .setting-row {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}}
input[type="checkbox"] {{
    width: auto !important;
    accent-color: var(--app-accent) !important;
}}

/* Fix single-line promo box to match boutique aesthetics safely */
a[href*="sporlyworks.com"] {{
    color: var(--app-accent) !important;
}}
div[style*="var(--cream)"] {{
    background: rgba(255,255,255, 0.5) !important;
    border: 1px solid rgba(0,0,0,0.04) !important;
    border-radius: 8px !important;
    margin: 0 24px 24px 24px !important;
    padding: 10px !important;
}}

.ma-footer {{
    background: transparent !important;
    border-top: none !important;
    color: rgba(0,0,0,0.4) !important;
    padding-bottom: 16px !important;
    font-size: 10px !important;
}}
.sdal-footer {{ display: none !important; }}
"""

extensions_to_inject = [
    "timestamp-converter", "link-checker", "color-palette-generator", "privacy-scanner", # flagship 4
    "cookie-manager", "css-inspector-pro", "json-formatter", "screenshot-capture",
    "qr-code-generator", "regex-tester", "markdown-preview", "word-counter",
    "time-tracker", "url-encoder-decoder"
]

import sys

# if passed args, override extensions list
if len(sys.argv) > 1:
    extensions_to_inject = sys.argv[1:]

for ext in extensions_to_inject:
    html_path = os.path.join(BASE_DIR, ext, "popup", "index.html")
    icon_path = os.path.join(BASE_DIR, ext, "icons", "icon128.png")
    if not os.path.exists(html_path):
        print(f"Skipping {ext}, no HTML found")
        continue

    dark_hex, accent_hex = ("#2E2522", "#2B3C4F") # generic fallback if error
    if os.path.exists(icon_path):
        dark_hex, accent_hex = get_dominant_colors(icon_path)

    with open(html_path, "r") as f:
        html = f.read()

    # Generate tailored CSS
    tailored_css = 精品_css_template.format(canvas="#F8F5EE", dark=dark_hex, accent=accent_hex)
    style_block = f"<style id='boutique-styling'>{tailored_css}</style>\n</head>"

    # Safe inject, replace previous boutique stylings if any
    if "boutique-styling" in html:
        html = re.sub(r"<style id='boutique-styling'>.*?</style>", "", html, flags=re.DOTALL)
        
    html = html.replace("</head>", style_block)
    
    with open(html_path, "w") as f:
        f.write(html)
        
    print(f"Boutique UI injected successfully into {ext} (Dark: {dark_hex}, Accent: {accent_hex})")
