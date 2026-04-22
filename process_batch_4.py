import os
import shutil
import subprocess

BATCH = {
    "base64-encoder": "sample_base64_1776115100843.png",
    "network-speed-test": "sample_networkspeed_1776115088964.png",
    "pomodoro-anywhere": "sample_pomodoro_1776115072823.png",
    "robots-viewer": "sample_robots_1776115060754.png",
    "bookmark-manager": "sample_bookmark_1776115046793.png",
    "site-speed-analyzer": "sample_sitespeed_1776115035606.png",
    "whois-lookup": "sample_whois_1776115021740.png",
    "reading-time-badge": "sample_readingtime_1776115007848.png",
    "diff-checker": "sample_diffchecker_1776114995506.png",
    "html-table-extractor": "sample_htmltable_1776114982426.png"
}

BRAIN_DIR = "/Users/davidmahler/.gemini/antigravity/brain/58f00244-3665-46fe-a8cf-782f3c9eb69a"
BASE_DIR = "/Users/davidmahler/Desktop/microAssets"

for ext_name, filename in BATCH.items():
    source_img = os.path.join(BRAIN_DIR, filename)
    target_icon_dir = os.path.join(BASE_DIR, ext_name, "icons")
    
    if not os.path.exists(target_icon_dir):
        os.makedirs(target_icon_dir, exist_ok=True)

    # Copy raw image to icon.png
    target_img = os.path.join(target_icon_dir, "icon.png")
    shutil.copy(source_img, target_img)
    print(f"Copied icon for {ext_name}")

    # Crop and resize the image properly (since it's a 1024x1024 generated image, crop to the center logo)
    print(f"Running crop for {ext_name}...")
    subprocess.run(["python3", "crop_icons.py", ext_name], cwd=BASE_DIR, check=True)

    # Inject the Boutique UI
    print(f"Injecting Boutique UI for {ext_name}...")
    subprocess.run(["python3", "inject_boutique_ui.py", ext_name], cwd=BASE_DIR, check=True)

# Update manifest and generate the resized icons
ext_args = list(BATCH.keys())
print("Rebuilding icons arrays...")
subprocess.run(["python3", "update_manifest_icons.py"] + ext_args, cwd=BASE_DIR, check=True)

print("Batch 4 injection complete. Ready for screenshots.")
