import os
import io
import json
import time
import concurrent.futures
from PIL import Image

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("google-genai not installed. Please install it.")
    exit(1)

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"

def generate_logo(ext_dir, ext_name, client):
    try:
        manifest_path = os.path.join(ext_dir, 'manifest.json')
        if not os.path.exists(manifest_path):
            return
            
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            
        real_name = manifest.get('name', ext_name).replace('—', '-').split('-')[0].strip()
        
        prompt = f"A flat-vector, monoline minimal geometry logo for a {real_name} browser extension. The design must focus entirely on the utility of the product. Organically incorporate a subtle scattering of tiny geometric spores or microscopic dots floating as a secondary accent. Strict earth tones (browns, muted greens, warm greys) and a cream (#F8F5EE) background. Absolutely NO mushroom shapes, NO 3D elements, NO gradients, NO AI slop, and NO text/letters."
        
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
                aspect_ratio="1:1"
            )
        )
        
        if result.generated_images:
            image_data = result.generated_images[0].image.image_bytes
            img = Image.open(io.BytesIO(image_data))
            
            # Ensure icons dir exists
            icons_dir = os.path.join(ext_dir, 'icons')
            os.makedirs(icons_dir, exist_ok=True)
            
            # Save original 1024x1024 to icons/icon128.png (or full_logo)
            # Actually let's name it icon_spore.png to keep master
            master_path = os.path.join(icons_dir, 'icon_spore.png')
            img.save(master_path)
            
            # Resize for icons/icon128.png and root icon16,48,128.png
            for size in [16, 48, 128]:
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(os.path.join(ext_dir, f'icon{size}.png'))
                if size == 128:
                    resized.save(os.path.join(icons_dir, 'icon128.png'))
            print(f"✅ Generated for {ext_name}")
        else:
            print(f"❌ Failed to generate for {ext_name}")
            
    except Exception as e:
        print(f"Error on {ext_name}: {e}")

def main():
    client = genai.Client()
    extensions = []
    
    for item in os.listdir(BASE_DIR):
        if item.endswith('-firefox') or item.endswith('-safari'):
            continue
        ext_dir = os.path.join(BASE_DIR, item)
        if os.path.isdir(ext_dir) and os.path.exists(os.path.join(ext_dir, 'manifest.json')):
            extensions.append((ext_dir, item))
            
    print(f"Found {len(extensions)} primary extensions.")
    
    # We use ThreadPoolExecutor to speed up API calls since they are I/O bound
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for ext_dir, ext_name in extensions:
            futures.append(executor.submit(generate_logo, ext_dir, ext_name, client))
            time.sleep(0.5) # Slight stagger 
        
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
