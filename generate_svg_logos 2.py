import os
import json
import subprocess
from openai import OpenAI
import concurrent.futures

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

if not OPENAI_KEY:
    print("❌ OPENAI_API_KEY not found in env.")
    exit(1)

client = OpenAI(api_key=OPENAI_KEY)

def generate_svg_logo(ext_dir, ext_name):
    master_svg_path = os.path.join(ext_dir, 'icons', 'icon_spore.svg')

    try:
        manifest_path = os.path.join(ext_dir, 'manifest.json')
        android_path = os.path.join(ext_dir, 'package.json')
        
        app_name = ext_name
        description = "A premium productivity application."
        
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
            
        print(f"Generating SVG Geometry for: {app_name}")
        
        # We explicitly ask GPT-4 to generate valid SVG geometry
        prompt = f"""You are an elite, world-class Master Brand Designer. Your task is to design a $100k, masterpiece, minimalist vector logo for an app called "{app_name}". 
        Description: {description}
        
        Constraints:
        1. Reply ONLY with valid raw <svg> XML code. No markdown, no triple backticks, no explanations.
        2. viewBox MUST be "0 0 512 512". 
        3. The background MUST be a `<rect width="512" height="512" fill="#F8F5EE"/>`.
        4. The logo must be an ultra-high-end, flat, geometric abstraction using thick lines (stroke-width: 30 to 40) and solid primitive geometry representing {app_name}'s function perfectly.
        5. Use predominantly "#2D2D2D" (charcoal black) for strokes, with exactly ONE tasteful accent fill color (e.g. bold orange "#FF5A36", deep blue "#1A56DB", vibrant green "#059669", etc) that conceptually matches the app.
        6. NO LETTERS, NO TEXT, NO WORDS anywhere.
        7. Must have absolute structural integrity so it remains perfectly legible when downscaled to 16x16.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        svg_code = response.choices[0].message.content.strip()
        if svg_code.startswith("```"):
            if "\n" in svg_code:
                svg_code = svg_code.split("\n", 1)[1]
        if svg_code.endswith("```"):
            svg_code = svg_code.rsplit("\n", 1)[0]
            
        icons_dir = os.path.join(ext_dir, 'icons')
        os.makedirs(icons_dir, exist_ok=True)
        
        with open(master_svg_path, 'w') as f:
            f.write(svg_code)
            
        # Render PNGs purely from the SVG to prevent blur using native macOS sips!
        for size in [16, 48, 128]:
            out_file = os.path.join(ext_dir, f'icon{size}.png')
            subprocess.run(["sips", "-z", str(size), str(size), "-s", "format", "png", master_svg_path, "--out", out_file], capture_output=True)
            if size == 128:
                subprocess.run(["sips", "-z", str(size), str(size), "-s", "format", "png", master_svg_path, "--out", os.path.join(icons_dir, 'icon128.png')], capture_output=True)
        
        # Render a 1024x1024 display master as png
        subprocess.run(["sips", "-z", "1024", "1024", "-s", "format", "png", master_svg_path, "--out", os.path.join(icons_dir, 'icon_spore.png')], capture_output=True)

        # Android deploy
        res_icon = os.path.join(ext_dir, 'android', 'app', 'src', 'main', 'res', 'mipmap-xxxhdpi')
        if os.path.isdir(res_icon):
            subprocess.run(["sips", "-z", "192", "192", "-s", "format", "png", master_svg_path, "--out", os.path.join(res_icon, 'ic_launcher.png')], capture_output=True)
            
        print(f"✅ SVG Masterpiece Generated & Deployed for {app_name}")
        
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
                
    print(f"Found {len(targets)} deployment targets. Launching Flawless SVG Overrides...")
    
    # We serialize heavily as GPT-4 can hit rate limits rapidly vs DALL-E
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for d, name in targets:
            futures.append(executor.submit(generate_svg_logo, d, name))
            
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
