import os
import glob
from PIL import Image

output_base = "/Users/davidmahler/Desktop/microAssets/sporlyworks_icons"
source_dir = "/Users/davidmahler/.gemini/antigravity/brain/fa2ef7d1-abd9-4d09-a47d-7b470dcc5fbc/"

images = {
    "jira-declutter": "jira_declutter_*.png",
    "json-csv-converter": "json_csv_converter_*.png",
    "json-formatter": "json_formatter_*.png",
    "json-path-finder": "json_path_finder_*.png",
    "jwt-decoder": "jwt_decoder_*.png",
    "link-checker": "link_checker_*.png",
    "linkedin-hide-feed": "linkedin_hide_feed_*.png",
    "llm-privacy-scrub": "llm_privacy_scrub_*.png",
    "lorem-ipsum-generator": "lorem_ipsum_gen_*.png",
    "markdown-preview": "markdown_preview_*.png",
    "meet-zoom-automute": "meet_zoom_automute_*.png",
    "meta-tag-editor": "meta_tag_editor_*.png",
    "microassets-master-suite": "microassets_master_*.png",
    "network-monitor-pro": "network_monitor_pro_*.png",
    "network-speed-test": "network_speed_test_*.png",
    "og-previewer": "og_previewer_*.png",
    "page-ruler": "page_ruler_*.png",
    "page-seo-analyzer": "page_seo_analyzer_*.png",
    "password-generator": "password_generator_*.png",
    "pomodoro-anywhere": "pomodoro_anywhere_*.png",
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

