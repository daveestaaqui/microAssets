import os
import json
import math
import hashlib
from PIL import Image, ImageDraw, ImageFont

# Deterministic earth-tone palette and cream background (100% Free Local Rendering)
CREAM = (248, 245, 238, 255)      # #F8F5EE
EARTH_TONES = [
    (32, 92, 64, 255),    # Forest green #205C40
    (58, 90, 64, 255),    # Muted sage #3A5A40
    (88, 47, 14, 255),    # Deep earth brown #582F0E
    (62, 77, 92, 255),    # Slate blue-grey #3E4D5C
    (110, 80, 50, 255),   # Warm wood #6E5032
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_initials(name):
    """Derive clean 2-letter initials from name."""
    words = [w for w in name.replace('—', ' ').replace('-', ' ').split() if w and w.lower() not in ('the', 'a', 'pro')]
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    elif len(words) == 1:
        return words[0][:2].upper()
    return "SW"

def generate_logo(ext_dir, ext_name, client=None):
    """Generate on-brand minimal spore logo locally using PIL. Zero paid API calls ($0.00)."""
    try:
        manifest_path = os.path.join(ext_dir, 'manifest.json')
        if not os.path.exists(manifest_path):
            return
            
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            
        real_name = manifest.get('name', ext_name).replace('—', '-').split('-')[0].strip()
        initials = get_initials(real_name)
        
        # Pick consistent earth tone based on extension name hash
        color_idx = int(hashlib.md5(real_name.encode()).hexdigest(), 16) % len(EARTH_TONES)
        primary_color = EARTH_TONES[color_idx]
        
        # Create 1024x1024 master canvas
        size = 1024
        img = Image.new("RGBA", (size, size), CREAM)
        draw = ImageDraw.Draw(img)
        
        # Draw soft outer margin
        pad = 120
        # Draw central rounded rectangle / badge
        draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=180, fill=primary_color)
        
        # Scatter subtle geometric "spore" dots organically around the badge perimeter
        h = int(hashlib.sha256(real_name.encode()).hexdigest(), 16)
        for i in range(16):
            angle = (i / 16.0) * 2 * math.pi + ((h >> (i % 32)) & 7) * 0.1
            dist = 420 + ((h >> ((i * 3) % 48)) & 15) * 4
            cx = int(size / 2 + dist * math.cos(angle))
            cy = int(size / 2 + dist * math.sin(angle))
            dot_radius = 8 + ((h >> (i % 24)) & 7)
            draw.ellipse([cx - dot_radius, cy - dot_radius, cx + dot_radius, cy + dot_radius], fill=primary_color)
            
        # Draw inner monoline ring
        inner_pad = pad + 40
        draw.rounded_rectangle([inner_pad, inner_pad, size - inner_pad, size - inner_pad], radius=140, outline=CREAM, width=8)
        
        # Draw initials centered
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 320)
        except Exception:
            font = ImageFont.load_default()
            
        box = draw.textbbox((0, 0), initials, font=font)
        tw = box[2] - box[0]
        th = box[3] - box[1]
        tx = (size - tw) / 2 - box[0]
        ty = (size - th) / 2 - box[1]
        draw.text((tx, ty), initials, fill=CREAM, font=font)
        
        # Save output icons
        icons_dir = os.path.join(ext_dir, 'icons')
        os.makedirs(icons_dir, exist_ok=True)
        master_path = os.path.join(icons_dir, 'icon_spore.png')
        img.save(master_path)
        
        for s in [16, 48, 128]:
            resized = img.resize((s, s), Image.Resampling.LANCZOS)
            resized.save(os.path.join(ext_dir, f'icon{s}.png'))
            if s == 128:
                resized.save(os.path.join(icons_dir, 'icon128.png'))
                
        print(f"✅ Locally generated free vector spore icon for {ext_name}")
    except Exception as e:
        print(f"Error on {ext_name}: {e}")

def main():
    extensions = []
    for item in os.listdir(BASE_DIR):
        if item.endswith('-firefox') or item.endswith('-safari') or item.startswith(('_', '.')):
            continue
        ext_dir = os.path.join(BASE_DIR, item)
        if os.path.isdir(ext_dir) and os.path.exists(os.path.join(ext_dir, 'manifest.json')):
            extensions.append((ext_dir, item))
            
    print(f"Found {len(extensions)} primary extensions. Generating local zero-cost icons...")
    for ext_dir, ext_name in extensions:
        generate_logo(ext_dir, ext_name)

if __name__ == "__main__":
    main()
