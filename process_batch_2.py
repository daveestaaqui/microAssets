import os
import glob
from PIL import Image

output_base = "/Users/davidmahler/Desktop/microAssets/sporlyworks_icons"

images = {
    "color-picker-eyedropper": "color_picker_eyedropper_*.png",
    "contract-highlighter": "contract_highlighter_*.png",
    "cookie-banner-rejector": "cookie_banner_reject_*.png",
    "cookie-manager": "cookie_manager_*.png",
    "copy-as-markdown": "copy_as_markdown_*.png",
    "crm-data-extractor": "crm_data_extractor_*.png",
    "css-box-shadow": "css_box_shadow_*.png",
    "css-flexbox-generator": "css_flexbox_gen_*.png",
    "css-gradient-generator": "css_gradient_gen_*.png",
    "css-grid-generator": "css_grid_gen_*.png",
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
