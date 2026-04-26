import os
import shutil
import subprocess

BATCH = {
    "html-table-extractor": "concept_htmltable2_1776115951191.png",
    "diff-checker": "concept_diffchecker2_1776115962601.png",
    "reading-time-badge": "concept_readingtime2_1776115974612.png",
    "whois-lookup": "concept_whois2_1776115987847.png",
    "site-speed-analyzer": "concept_sitespeed2_1776116001277.png",
    "bookmark-manager": "concept_bookmark_1776115877533.png",
    "robots-viewer": "concept_robots_1776115889208.png",
    "pomodoro-anywhere": "concept_pomodoro_1776115901748.png",
    "network-speed-test": "concept_networkspeed_1776115913730.png",
    "base64-encoder": "concept_base64_1776115923631.png"
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

print("Batch 7 injection complete. Ready for screenshots.")
