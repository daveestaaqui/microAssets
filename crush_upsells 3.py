import os
import re

base_dir = '/Users/davidmahler/Desktop/microAssets'
extensions = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')]

for ext in extensions:
    popup_path = os.path.join(base_dir, ext, 'popup', 'index.html')
    if os.path.exists(popup_path):
        with open(popup_path, 'r') as f:
            html = f.read()
            
        # 1. Remove ANY emoji (💎 or 👑) from the file (we'll just target the prominent ones for upsells, 
        # but regex for all isn't strictly necessary since we know what he saw. Let's just strip diamonds and crowns)
        html = html.replace('💎', '').replace('👑', '')

        # 2. We need to find elements with class *upsell* or id *upsell* 
        # and replace them with a tiny, clean, single line "Get Pro Access →"
        
        # Regex to find <div class=".*upsell.*">...</div> or <div id=".*upsell.*">...</div>
        # This is a bit tricky with regex for multi-line HTML, so we'll use a specific replacement 
        # for known tags like <div class="sdal-upsell"> and <div id="ma-pro-upsell" ...>
        
        clean_upsell = '''<div style="margin-top:12px;padding:8px;background:var(--cream);border:1px solid rgba(0,0,0,0.1);border-radius:4px;text-align:center;">
    <a href="https://sporlyworks.com/pro" style="color:var(--text);font-size:11px;font-weight:600;text-decoration:none;display:block;">Get Pro Access &rarr;</a>
</div>'''

        # Replace standard known blocks.
        html = re.sub(r'<div class="sdal-upsell">.*?</div>', clean_upsell, html, flags=re.DOTALL)
        html = re.sub(r'<div id="ma-pro-upsell"[^>]*>.*?</div>', clean_upsell, html, flags=re.DOTALL)
        html = re.sub(r'<div class="upsell-container[^>]*>.*?</div>', clean_upsell, html, flags=re.DOTALL)
        
        # Write back
        with open(popup_path, 'w') as f:
            f.write(html)

print("Upsells crushed globally. 💎 removed.")
