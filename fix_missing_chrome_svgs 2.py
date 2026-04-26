import os
import json
import subprocess
from openai import OpenAI
import concurrent.futures

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

client = OpenAI(api_key=OPENAI_KEY)

targets = ['clipboard-history', 'form-filler-pro', 'meta-tag-editor', 'password-generator', 'quick-notepad', 'reading-mode', 'url-shortener', 'word-counter']

def generate_svg_logo(ext_dir, ext_name):
    master_svg_path = os.path.join(ext_dir, 'icons', 'icon_spore.svg')

    try:
        manifest_path = os.path.join(ext_dir, 'manifest.json')
        app_name = ext_name
        description = "A premium productivity application."
        
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            app_name = manifest.get('name', ext_name).replace('—', '-').split('-')[0].strip().lower()
            description = manifest.get('description', description)
            
        print(f"Generating SVG Geometry for: {app_name}")
        
        prompt = f"""You are an elite, world-class Master Brand Designer. Your task is to design a $100k, masterpiece, minimalist vector logo for an app called "{app_name}". 
        Description: {description}
        
        Constraints:
        1. Reply ONLY with valid raw <svg> XML code. No markdown, no triple backticks, no explanations.
        2. viewBox MUST be "0 0 512 512". 
        3. The background MUST be a `<rect width="512" height="512" fill="#F8F5EE"/>`.
        4. The logo must be an ultra-high-end, flat, geometric abstraction using thick lines (stroke-width: 30 to 40) and solid primitive geometry representing {app_name}'s function perfectly.
        5. Use predominantly "#2D2D2D" (charcoal black) for strokes, with exactly ONE tasteful accent fill color (e.g. bold orange "#FF5A36", deep blue "#1A56DB", vibrant green "#059669") that conceptually matches the app.
        6. NO LETTERS, NO TEXT, NO WORDS anywhere.
        7. Must have absolute structural integrity so it remains perfectly legible when downscaled to 16x16.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        svg_code = response.choices[0].message.content.strip()
        if svg_code.startswith("```"):
            svg_code = svg_code.split("\n", 1)[1]
        if svg_code.endswith("```"):
            svg_code = svg_code.rsplit("\n", 1)[0]
            
        icons_dir = os.path.join(ext_dir, 'icons')
        os.makedirs(icons_dir, exist_ok=True)
        
        with open(master_svg_path, 'w') as f:
            f.write(svg_code)
            
        for size in [16, 48, 128]:
            out_file = os.path.join(ext_dir, f'icon{size}.png')
            subprocess.run(["sips", "-z", str(size), str(size), "-s", "format", "png", master_svg_path, "--out", out_file], capture_output=True)
            if size == 128:
                subprocess.run(["sips", "-z", str(size), str(size), "-s", "format", "png", master_svg_path, "--out", os.path.join(icons_dir, 'icon128.png')], capture_output=True)
        
        subprocess.run(["sips", "-z", "1024", "1024", "-s", "format", "png", master_svg_path, "--out", os.path.join(icons_dir, 'icon_spore.png')], capture_output=True)

        print(f"✅ Generated & Deployed for {ext_name}")
        
    except Exception as e:
        print(f"❌ Error on {ext_name}: {e}")

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = []
    for t in targets:
        d = os.path.join(BASE_DIR, t)
        futures.append(executor.submit(generate_svg_logo, d, t))
    concurrent.futures.wait(futures)
