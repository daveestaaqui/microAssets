import os
import shutil
import subprocess

BATCH = {
    "css-grid-generator": "concept_cssgrid_1776115400010_1776115681618.png",
    "css-gradient-generator": "concept_cssgrad_1776115400009_1776115666702.png",
    "css-flexbox-generator": "concept_cssflex_1776115400008_1776115653085.png",
    "css-box-shadow": "concept_cssbox_1776115400007_1776115640958.png",
    "crm-data-extractor": "concept_crm_1776115400006_1776115626633.png",
    "copy-as-markdown": "concept_copymd_1776115400005_1776115614221.png",
    "cookie-banner-rejector": "concept_cookiebanner_1776115400004_1776115601797.png",
    "contract-highlighter": "concept_contract_1776115400003_1776115591233.png",
    "code-snippet-manager": "concept_codesnippet_1776115400002_1776115578326.png",
    "clipboard-history": "concept_clipboard_1776115400001_1776115565442.png"
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

print("Batch 6 injection complete. Ready for screenshots.")
