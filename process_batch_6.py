import os
import glob
from PIL import Image

output_base = "/Users/davidmahler/Desktop/microAssets/sporlyworks_icons"
source_dir = "/Users/davidmahler/.gemini/antigravity/brain/fa2ef7d1-abd9-4d09-a47d-7b470dcc5fbc/"

images = {
    "url-shortener": "url_shortener_*.png",
    "user-agent-switcher": "user_agent_switcher_*.png",
    "wayback-machine-quick": "wayback_machine_quick_*.png",
    "wcag-auditor": "wcag_auditor_*.png",
    "website-monitor-pro": "website_monitor_pro_*.png",
    "whois-lookup": "whois_lookup_*.png",
    "word-counter": "word_counter_*.png",
}

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

