import os
import glob
from PIL import Image

output_base = "/Users/davidmahler/Desktop/microAssets/sporlyworks_icons"
source_dir = "/Users/davidmahler/.gemini/antigravity/brain/fa2ef7d1-abd9-4d09-a47d-7b470dcc5fbc/"

images = {
    "css-minifier": "css_minifier_*.png",
    "dark-mode-everywhere": "dark_mode_everywhere_*.png",
    "diff-checker": "diff_checker_*.png",
    "diff-viewer": "diff_viewer_*.png",
    "dom-editor-pro": "dom_editor_pro_*.png",
    "email-template-builder": "email_template_bldr_*.png",
    "favicon-grabber": "favicon_grabber_*.png",
    "font-identifier": "font_identifier_*.png",
    "form-filler-pro": "form_filler_pro_*.png",
    "gdocs-focus-mode": "gdocs_focus_mode_*.png",
    "github-line-numbers": "github_line_numbers_*.png",
    "github-quick-stats": "github_quick_stats_*.png",
    "google-dark-search": "google_dark_search_*.png",
    "hash-generator": "hash_generator_*.png",
    "html-table-extractor": "html_table_extract_*.png",
    "http-headers": "http_headers_*.png",
    "http-status-checker": "http_status_check_*.png",
    "instagram-clean-feed": "instagram_clean_*.png",
    "invoice-extractor": "invoice_extractor_*.png",
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

