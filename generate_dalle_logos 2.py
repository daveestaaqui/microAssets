import os
import json
import requests
import io
from PIL import Image, ImageEnhance
from openai import OpenAI
import concurrent.futures

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

if not OPENAI_KEY:
    print("❌ OPENAI_API_KEY not found in env.")
    exit(1)

client = OpenAI(api_key=OPENAI_KEY)

def generate_logo(ext_dir, ext_name):
    master_path = os.path.join(ext_dir, 'icons', 'icon_spore.png')

    try:
        manifest_path = os.path.join(ext_dir, 'manifest.json')
        android_path = os.path.join(ext_dir, 'package.json')
        
        app_name = ext_name
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            app_name = manifest.get('name', ext_name).replace('—', '-').split('-')[0].strip().lower()
        elif os.path.exists(android_path):
            with open(android_path, 'r') as f:
                manifest = json.load(f)
            app_name = manifest.get('name', ext_name).replace('-', ' ').lower()
            
        print(f"Generating BOLD structurally scalable logic for: {app_name}")
        
        keywords = app_name.replace('app', '').replace('extension', '').replace('tool', '')
        
        prompt = f"An ultra-premium, ultra-minimalist, flat abstract SaaS app icon representing '{keywords}'. STRICTLY NO LETTERS, NO ALPHABET CHARACTERS, NO WORDS. ZERO TEXT. Avoid all generic clip-art. The design must be a purely abstract, bold, chunky geometric mark. Use ONLY thick lines and large solid shapes. No thin lines, no intricate details. Must be highly legible at tiny 16x16 scale. Include subtle spore-dot accents. Center the logo perfectly on a luxurious cream-colored background (#F8F5EE). Award-winning structural minimalism."
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard", 
            n=1,
            response_format="url"
        )
        
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        
        icons_dir = os.path.join(ext_dir, 'icons')
        os.makedirs(icons_dir, exist_ok=True)
        img.save(master_path)
        
        w, h = img.size
        
        # --- 128px NORMAL SCALE ---
        img.resize((128, 128), Image.Resampling.LANCZOS).save(os.path.join(ext_dir, 'icon128.png'))
        img.resize((128, 128), Image.Resampling.LANCZOS).save(os.path.join(icons_dir, 'icon128.png'))
        
        # --- 48px: 60% CROP & ENHANCE ---
        crop_size_48 = int(w * 0.6)
        c48_left = (w - crop_size_48) // 2
        c48_top = (h - crop_size_48) // 2
        cropped_48 = img.crop((c48_left, c48_top, c48_left + crop_size_48, c48_top + crop_size_48))
        res_48 = cropped_48.resize((48, 48), Image.Resampling.LANCZOS)
        ImageEnhance.Contrast(res_48).enhance(1.5).save(os.path.join(ext_dir, 'icon48.png'))
        
        # --- 16px: 40% EXTREME CROP & ENHANCE ---
        crop_size_16 = int(w * 0.4)
        c16_left = (w - crop_size_16) // 2
        c16_top = (h - crop_size_16) // 2
        cropped_16 = img.crop((c16_left, c16_top, c16_left + crop_size_16, c16_top + crop_size_16))
        res_16 = cropped_16.resize((16, 16), Image.Resampling.LANCZOS)
        ImageEnhance.Contrast(res_16).enhance(2.0).save(os.path.join(ext_dir, 'icon16.png'))
        
        # Android deploy
        res_icon = os.path.join(ext_dir, 'android', 'app', 'src', 'main', 'res', 'mipmap-xxxhdpi')
        if os.path.isdir(res_icon):
            img.resize((192, 192), Image.Resampling.LANCZOS).save(os.path.join(res_icon, 'ic_launcher.png'))
            
        print(f"✅ BOLD Optical Extract generated for {app_name}")
        
    except Exception as e:
        print(f"❌ Error on {ext_name}: {e}")

def main():
    targets = []
    
    for item in os.listdir(BASE_DIR):
        if item.endswith('-firefox') or item.endswith('-safari'):
            continue
        ext_dir = os.path.join(BASE_DIR, item)
        if os.path.isdir(ext_dir) and os.path.exists(os.path.join(ext_dir, 'manifest.json')):
            targets.append((ext_dir, item))
            
    android_dir = os.path.join(BASE_DIR, "_b2b_android")
    if os.path.isdir(android_dir):
        for item in os.listdir(android_dir):
            app_dir = os.path.join(android_dir, item)
            if os.path.isdir(app_dir) and os.path.exists(os.path.join(app_dir, 'capacitor.config.json')):
                targets.append((app_dir, item))
                
    print(f"Found {len(targets)} deployment targets. Launching Optical Center-Crop Overrides...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for d, name in targets:
            futures.append(executor.submit(generate_logo, d, name))
            
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
