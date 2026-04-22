import os
import re
import sys
from collections import Counter
from PIL import Image

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"

def get_dominant_colors(image_path, num_colors=2):
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        return ["#2E2522", "#6C7A68"] # Fallback earth-tone dark and accent

    img = img.resize((100, 100))
    pixels = list(img.getdata())
    
    def is_light(c): return (c[0]*0.299 + c[1]*0.587 + c[2]*0.114) > 200
    
    filtered_pixels = [p for p in pixels if not is_light(p)]

    if not filtered_pixels:
        return ["#2E2522", "#6C7A68"]

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
    accent_c = unique_colors[1] if len(unique_colors) > 1 else unique_colors[0]
    
    # Enforce dark text rule for legibility (lum < 100)
    if luminance(dark_c) > 100:
        factor = 80 / max(luminance(dark_c), 1)
        dark_c = (int(dark_c[0] * factor), int(dark_c[1] * factor), int(dark_c[2] * factor))
        
    dark_hex = f"#{dark_c[0]:02x}{dark_c[1]:02x}{dark_c[2]:02x}"
    accent_hex = f"#{accent_c[0]:02x}{accent_c[1]:02x}{accent_c[2]:02x}"
    
    return dark_hex, accent_hex

SPORE_CSS_TEMPLATE = """
/* 🍄 SPORE UI OVERRIDE: Premium Minimal Geometry */
:root {{
    --app-canvas: #F8F5EE;
    --app-dark: {dark};
    --app-accent: {accent};
}}

body {{
    background-color: var(--app-canvas) !important;
    color: var(--app-dark) !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif !important;
    letter-spacing: -0.015em !important;
    width: 320px;
    margin: 0;
    
    /* Subtle geometric spore background */
    background-image: radial-gradient(rgba(0,0,0, 0.03) 1px, transparent 1px) !important;
    background-size: 24px 24px !important;
}}

/* Header */
.sdal-header {{
    background: transparent !important;
    box-shadow: none !important;
    border-bottom: 1px solid rgba(0,0,0,0.1) !important;
    padding: 32px 24px 20px 24px !important;
    margin-bottom: 0px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 0 !important;
}}
.sdal-logo {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}}
.sdal-logo span {{
    font-weight: 700 !important;
    font-size: 20px !important;
    color: var(--app-dark) !important;
    letter-spacing: -0.03em !important;
    margin-top: 16px !important;
    margin-left: 0 !important;
    text-align: center !important;
}}
.sdal-img {{
    width: 80px !important;
    height: 80px !important;
    border-radius: 0 !important;
    border: none !important;
    box-shadow: none !important;
    display: block !important;
}}

/* Body */
.sdal-body {{
    padding: 24px !important;
    border-radius: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 20px !important;
    box-shadow: none !important;
}}

/* Typography */
h1, h2, h3, h4 {{
    color: var(--app-dark) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}}

/* High-contrast strict inputs */
input, textarea, select {{
    background: var(--app-canvas) !important;
    border: 1px solid var(--app-dark) !important;
    color: var(--app-dark) !important;
    border-radius: 0 !important;
    padding: 14px 16px !important;
    font-size: 14px !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
    box-sizing: border-box !important;
    width: 100% !important;
}}
input:focus, textarea:focus, select:focus {{
    border: 2px solid var(--app-dark) !important;
    outline: none !important;
    background: #ffffff !important;
    padding: 13px 15px !important; /* adjust for border width */
}}

/* Monoline Action Buttons */
button, .sdal-btn {{
    background: var(--app-dark) !important;
    color: var(--app-canvas) !important;
    border: none !important;
    border-radius: 0 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 16px 20px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
    letter-spacing: -0.01em !important;
    cursor: pointer !important;
    width: 100% !important;
    text-align: center !important;
    box-sizing: border-box !important;
}}
button:hover, .sdal-btn:hover {{
    background: var(--app-accent) !important;
    transform: translateY(-1px) !important;
}}

/* Checkboxes & Toggles */
.option-row, .setting-row {{
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
}}
input[type="checkbox"] {{
    width: 18px !important;
    height: 18px !important;
    accent-color: var(--app-dark) !important;
    border: 1px solid var(--app-dark) !important;
    border-radius: 0 !important;
    -webkit-appearance: none;
    background-color: var(--app-canvas);
    cursor: pointer !important;
}}
input[type="checkbox"]:checked {{
    background-color: var(--app-dark);
}}

/* Promo boxes */
a[href*="sporlyworks.com"] {{
    color: var(--app-accent) !important;
    font-weight: bold !important;
}}
div[style*="var(--cream)"] {{
    background: transparent !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
    border-radius: 0 !important;
    margin: 0 24px 24px 24px !important;
    padding: 16px !important;
}}

.ma-footer {{
    background: transparent !important;
    border-top: 1px solid rgba(0,0,0,0.1) !important;
    color: var(--app-dark) !important;
    padding: 16px !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    opacity: 0.7 !important;
}}
.sdal-footer {{ display: none !important; }}
"""

def main():
    extensions_to_inject = []
    
    if len(sys.argv) > 1:
        extensions_to_inject = sys.argv[1:]
    else:
        # Load all core extensions
        list_file = os.path.join(BASE_DIR, "core_extensions.txt")
        if os.path.exists(list_file):
            with open(list_file, "r") as f:
                extensions_to_inject = [line.strip() for line in f if line.strip()]
    
    # Also append their -firefox equivalents automatically
    all_targets = []
    for ext in extensions_to_inject:
        all_targets.append(ext)
        all_targets.append(ext + "-firefox")
        all_targets.append(ext + "-safari")

    success_count = 0
    for ext in all_targets:
        dir_path = os.path.join(BASE_DIR, ext)
        if not os.path.exists(dir_path):
            continue
            
        html_path = os.path.join(dir_path, "popup", "index.html")
        alt_html_path = os.path.join(dir_path, "popup", "popup.html")
        
        target_html = html_path if os.path.exists(html_path) else alt_html_path
        if not os.path.exists(target_html):
            continue

        icon_path = os.path.join(dir_path, "icons", "icon128.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(dir_path, "icon128.png")

        dark_hex, accent_hex = ("#2E2522", "#6C7A68")
        if os.path.exists(icon_path):
            dark_hex, accent_hex = get_dominant_colors(icon_path)

        with open(target_html, "r") as f:
            html = f.read()

        # HTML Scrubbing Pass: Remove all Pro links and diamonds
        html = re.sub(r'<!-- Stripe Pro Upsell.*?-->', '', html, flags=re.DOTALL)
        html = re.sub(r'<div[^>]*>\s*<a href="https://sporlyworks\.com/pro".*?</div>', '', html, flags=re.DOTALL)
        html = html.replace('💎 Get Pro Access', '')
        html = html.replace('💎', '')
        # Some blocks might not have the comment but have the link
        html = re.sub(r'<a[^>]*Get Pro Access[^>]*>.*?</a>', '', html, flags=re.IGNORECASE)

        # Generate tailored CSS
        tailored_css = SPORE_CSS_TEMPLATE.format(dark=dark_hex, accent=accent_hex)
        style_block = f"<style id='boutique-styling'>{tailored_css}</style>\n</head>"

        # Safe inject
        if "boutique-styling" in html:
            html = re.sub(r"<style id='boutique-styling'>.*?</style>", "", html, flags=re.DOTALL)
            
        html = html.replace("</head>", style_block)
        
        with open(target_html, "w") as f:
            f.write(html)
            
        success_count += 1
        
    print(f"Inject Spores UI complete. Processed {success_count} extensions.")

if __name__ == "__main__":
    main()
