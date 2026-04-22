import os
import glob
import re
import hashlib
import json

BASE_DIR = '/Users/davidmahler/Desktop/microAssets'
EARTH_TONES = [
    (34, 59, 50),   # Deep Pine
    (156, 74, 56),  # Terracotta
    (44, 59, 71),   # Slate Navy
    (82, 92, 64),   # Olive Drab
    (45, 39, 36),   # Espresso
    (139, 104, 66), # Warm Mustard/Ochre
    (93, 64, 80),   # Muted Plum
    (74, 72, 67)    # Warm Stone
]

def hex_clr(c):
    return "#{:02x}{:02x}{:02x}".format(c[0], c[1], c[2])

def clean_html(html_path):
    with open(html_path, 'r') as f:
        html = f.read()

    # Clean up "💎 Get Pro Access" and similar huge buttons to be minimalist and one-line.
    # We replace the diamond and any multi-line formatting.
    html = re.sub(r'💎\s*Get Pro Access', 'Upgrade to Pro', html)
    html = re.sub(r'👑\s*Go Premium', 'Upgrade to Pro', html)
    
    with open(html_path, 'w') as f:
        f.write(html)

def generate_css(earth_tone):
    primary = hex_clr(earth_tone)
    
    return f"""
/* 🏛️ Solid Pure Minimalist UI */
* {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', system-ui, sans-serif; }}
body {{ background: #fdfdfc !important; color: #1a1a1a !important; display: flex; flex-direction: column; }}

/* Larger logo, high-end header branding */
.sdal-header {{
    background: #ffffff !important; padding: 18px 24px !important; box-shadow: none !important;
    border-bottom: 1px solid #f0f0f0 !important; margin-bottom: 24px !important;
    display: flex !important; align-items: center !important; gap: 16px !important;
}}
.sdal-img {{
    width: 40px !important; height: 40px !important; border-radius: 8px !important;
    box-shadow: none !important; object-fit: contain !important; flex-shrink: 0;
}}
.sdal-logo {{ display: flex !important; align-items: center !important; gap: 16px !important; flex-direction: row !important; }}
.sdal-logo span {{ font-size: 18px !important; font-weight: 600 !important; letter-spacing: -0.015em !important; color: #1a1a1a !important; text-shadow: none !important; }}

h3, h2, h1 {{ color: #1a1a1a !important; background: none !important; -webkit-text-fill-color: #1a1a1a !important; font-weight: 600 !important; font-size: 14px !important; letter-spacing: -0.01em !important; margin-bottom: 8px; }}

input, textarea, select {{
    width: 100%; padding: 10px 14px; background: #ffffff !important; color: #1a1a1a !important;
    border: 1px solid #e5e5e5 !important; border-radius: 6px !important; margin-bottom: 16px;
    font-size: 13px; outline: none; transition: border-color 0.15s ease;
    box-shadow: none !important;
}}
input:focus, textarea:focus, select:focus {{ border-color: {primary} !important; }}

button, .sdal-btn {{
    width: 100%; padding: 10px 16px; background: {primary} !important; color: #ffffff !important;
    border: none !important; border-radius: 6px !important; font-weight: 500; font-size: 13px;
    cursor: pointer; margin-bottom: 12px; box-shadow: none !important;
    display: flex; justify-content: center; align-items: center; gap: 8px;
    transition: filter 0.15s ease;
}}
button:hover, .sdal-btn:hover {{ filter: brightness(0.9); transform: none !important; }}

/* Restrain the Pro button */
.pro-btn, #pro-btn, [class*="pro-"] {{
    background: transparent !important; color: {primary} !important;
    border: 1px solid {primary} !important; 
    padding: 8px 12px !important; font-size: 12px !important;
    margin-top: 16px !important; white-space: nowrap !important;
}}

pre {{ padding: 12px; background: #f5f5f5 !important; color: #333333 !important; border: 1px solid #e5e5e5 !important; border-radius: 6px !important; font-family: 'JetBrains Mono', monospace; font-size: 11px; white-space: pre-wrap; word-break: break-all; margin-bottom: 12px; }}
"""

def process(ext_dir):
    popup_css_path = os.path.join(ext_dir, 'popup', 'popup.css')
    html_path = os.path.join(ext_dir, 'popup', 'index.html')
    manifest_path = os.path.join(ext_dir, "manifest.json")
    
    if not os.path.exists(popup_css_path):
        return
        
    try:
        with open(manifest_path, 'r') as f:
            name = json.load(f).get('name', os.path.basename(ext_dir))
    except:
        name = os.path.basename(ext_dir)
        
    seed = name.lower().strip()
    brand_color = EARTH_TONES[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(EARTH_TONES)]
    
    with open(popup_css_path, 'r') as f:
        css = f.read()
        
    # Clean previous injected styles
    css = re.sub(r'/\* 🌟 Standardized Design Injection \*/.*', '', css, flags=re.DOTALL)
    css = re.sub(r'/\* 💥 SLAM UI Overrides \*/.*', '', css, flags=re.DOTALL)
    css = re.sub(r'/\* 🌍 Elite Earth Tone UI \*/.*', '', css, flags=re.DOTALL)
    css = re.sub(r'/\* 🏛️ Truly Elite Geometric UI \*/.*', '', css, flags=re.DOTALL)
    css = re.sub(r'/\* 🏛️ Solid Pure Minimalist UI \*/.*', '', css, flags=re.DOTALL)
    
    css += "\n" + generate_css(brand_color)
    
    with open(popup_css_path, 'w') as f:
        f.write(css)

    if os.path.exists(html_path):
        clean_html(html_path)

def main():
    folders = [f for f in glob.glob(os.path.join(BASE_DIR, '*')) if os.path.isdir(f)]
    for folder in folders:
        process(folder)

if __name__ == '__main__':
    main()
