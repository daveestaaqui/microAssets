import os
import glob
from PIL import Image

output_base = "/Users/davidmahler/Desktop/microAssets/sporlyworks_icons"

images = {
    "ai-content-bouncer": "ai_content_bouncer_*.png",
    "amazon-fake-review-skimmer": "amazon_fake_review_*.png",
    "amazon-wide-mode": "amazon_wide_mode_*.png",
    "api-tester-pro": "api_tester_pro_*.png",
    "base64-encoder": "base64_encoder_*.png",
    "bookmark-manager": "bookmark_manager_*.png",
    "carbon-footprint-checker": "carbon_footprint_checker_*.png",
    "clipboard-history": "clipboard_history_*.png",
    "code-snippet-manager": "code_snippet_manager_*.png",
    "color-palette-generator": "color_palette_generator_*.png"
}

source_dir = "/Users/davidmahler/.gemini/antigravity/brain/fa2ef7d1-abd9-4d09-a47d-7b470dcc5fbc/"

def strip_white_bg(img_path, out_path):
    try:
        img = Image.open(img_path).convert("RGBA")
        data = img.getdata()
        new_data = []
        for item in data:
            if item[0] > 235 and item[1] > 235 and item[2] > 235:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        img.save(out_path, "PNG")
        print(f"Saved: {out_path}")
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

for folder, pattern in images.items():
    matches = glob.glob(os.path.join(source_dir, pattern))
    if matches:
        img_file = matches[0]
        # Save to base extension folder
        out1 = os.path.join(output_base, folder, "icon.png")
        strip_white_bg(img_file, out1)
        
        # Save to firefox sibling if we want
        out2 = os.path.join(output_base, f"{folder}-firefox", "icon.png")
        strip_white_bg(img_file, out2)
