import os
import json
from openai import OpenAI
import subprocess

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_KEY)

def generate_svg_logo(app_name, description):
    prompt = f"""You are an elite, world-class Master Brand Designer. Your task is to design a $100k, masterpiece, minimalist vector logo for a Chrome Extension called "{app_name}". 
    Description: {description}
    
    Constraints:
    1. Reply ONLY with valid raw <svg> XML code. No markdown, no triple backticks, no explanations.
    2. viewBox MUST be "0 0 512 512". 
    3. The background MUST be a `<rect width="512" height="512" fill="#F8F5EE"/>`.
    4. The logo must be an ultra-high-end, flat, geometric abstraction using thick lines (stroke-width: 30 to 40) and solid primitive geometry.
    5. Use predominantly "#2D2D2D" (charcoal black) for strokes, with exactly one tasteful accent fill color (e.g. bold orange "#FF5A36", deep blue "#1A56DB", or vibrant green "#059669") that conceptually matches the app.
    6. NO LETTERS, NO TEXT, NO WORDS anywhere.
    7. Must have absolute structural integrity so it remains perfectly legible when downscaled to 16x16.
    """

    print("Generating Master SVG...")
    response = client.chat.completions.create(
        model="gpt-4", # Or gpt-4o/gpt-4-turbo
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    svg_code = response.choices[0].message.content.strip()
    
    # Remove markdown if it accidentally added it
    if svg_code.startswith("```"):
        svg_code = svg_code.split("\n", 1)[1]
    if svg_code.endswith("```"):
        svg_code = svg_code.rsplit("\n", 1)[0]
        
    with open("masterpiece_test.svg", "w") as f:
        f.write(svg_code)
        
    print("SVG Saved. Rasterizing cleanly via sips...")
    # Render crisp PNGs
    for size in [1024, 128, 48, 16]:
        out_name = f"masterpiece_test_{size}.png"
        subprocess.run(["sips", "-z", str(size), str(size), "-s", "format", "png", "masterpiece_test.svg", "--out", out_name], capture_output=True)
        print(f"Generated {out_name}")

generate_svg_logo("Color Picker Eyedropper", "A professional tool for web developers to pick colors from any webpage, extract HEX/RGB codes, and build beautiful color palettes dynamically.")
