import os
import json
import requests
import io
from PIL import Image, ImageFilter
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
        description = "A powerful productivity tool."
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            app_name = manifest.get('name', ext_name).replace('—', '-').split('-')[0].strip().lower()
            description = manifest.get('description', description)
        elif os.path.exists(android_path):
            with open(android_path, 'r') as f:
                manifest = json.load(f)
            app_name = manifest.get('name', ext_name).replace('-', ' ').lower()
            description = manifest.get('description', description)
            
        print(f"Generating $10k Masterpiece for: {app_name}")
        
        prompt = f"""Act as a world-class, multi-award-winning brand architect. I need a $10,000 masterpiece minimalist logo for my application. 
        App Name: {app_name}
        App Description: {description}
        
        Strict Design Principles:
        1. ZERO TEXT, ZERO LETTERS, NO WORDS.
        2. The design must be a purely abstract, perfectly symmetric, flat geometric composition.
        3. Use massive, heavy shapes with extremely thick stroke weights and wide negative space. It must be instantly recognizable and highly legible even if scaled down to microscopic sizes. Avoid complex intricacies.
        4. Do not use gradients, 3D effects, or thin lines. Solid flat colors only. 
        5. Use exactly two colors: #2D2D2D (charcoal black) for the base geometric structure, and one single high-contrast accent color that conceptually fits the tool. Use a solid cream #F8F5EE background.
        6. Deliver an architectural, monolithic icon that implies the tool's core function through brilliant geometric abstraction. No slop."""
        
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
        
        # Standard downscaling, using ImageFilter on tiny sizes to retain punchy contrast
        img.resize((128, 128), Image.Resampling.LANCZOS).save(os.path.join(ext_dir, 'icon128.png'))
        img.resize((128, 128), Image.Resampling.LANCZOS).save(os.path.join(icons_dir, 'icon128.png'))
        
        res_48 = img.resize((48, 48), Image.Resampling.LANCZOS).filter(ImageFilter.SHARPEN)
        res_48.save(os.path.join(ext_dir, 'icon48.png'))
        
        res_16 = img.resize((16, 16), Image.Resampling.LANCZOS).filter(ImageFilter.SHARPEN)
        res_16.save(os.path.join(ext_dir, 'icon16.png'))
        
        res_icon = os.path.join(ext_dir, 'android', 'app', 'src', 'main', 'res', 'mipmap-xxxhdpi')
        if os.path.isdir(res_icon):
            img.resize((192, 192), Image.Resampling.LANCZOS).save(os.path.join(res_icon, 'ic_launcher.png'))
            
        print(f"✅ $10k Masterpiece Deployed for {app_name}")
        
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
                
    print(f"Found {len(targets)} deployment targets. Launching Ultimate DALL-E Sweep...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for d, name in targets:
            futures.append(executor.submit(generate_logo, d, name))
            
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
