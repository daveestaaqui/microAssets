import os
import glob
from PIL import Image

output_base = "/Users/davidmahler/Desktop/microAssets/sporlyworks_icons"
source_dir = "/Users/davidmahler/.gemini/antigravity/brain/fa2ef7d1-abd9-4d09-a47d-7b470dcc5fbc/"

images = {
    "privacy-scanner": "privacy_scanner_*.png",
    "qr-code-generator": "qr_code_generator_*.png",
    "quick-note-taker": "quick_note_taker_*.png",
    "quick-notepad": "quick_notepad_*.png",
    "reading-mode": "reading_mode_*.png",
    "reading-time-badge": "reading_time_badge_*.png",
    "reddit-redirect": "reddit_redirect_*.png",
    "regex-tester": "regex_tester_*.png",
    "responsive-viewer": "responsive_viewer_*.png",
    "robots-viewer": "robots_viewer_*.png",
    "screenshot-capture": "screenshot_capture_*.png",
    "seo-content-pro": "seo_content_pro_*.png",
    "site-speed-analyzer": "site_speed_analyzer_*.png",
    "sponsor-skipper": "sponsor_skipper_*.png",
    "tab-groups-saver": "tab_groups_saver_*.png",
    "tab-suspender": "tab_suspender_*.png",
    "text-case-converter": "text_case_converter_*.png",
    "time-tracker": "time_tracker_*.png",
    "timestamp-converter": "timestamp_converter_*.png",
    "url-encoder-decoder": "url_encoder_decoder_*.png",
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

