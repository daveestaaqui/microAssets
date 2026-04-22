import os
import shutil
import subprocess

BATCH = {
    "password-generator": "sample_password_1776114644431.png",
    "dom-editor-pro": "sample_dom_1776114659870.png",
    "favicon-grabber": "sample_favicon_1776114671422.png",
    "css-minifier": "sample_cssmin_1776114685333.png",
    "tab-groups-saver": "sample_tabgroups_1776114697167.png",
    "email-template-builder": "sample_email_1776114710357.png",
    "font-identifier": "sample_font_1776114722254.png",
    "seo-content-pro": "sample_seo_1776114733937.png",
    "youtube-pip": "sample_pip_1776114750081.png",
    "color-picker": "sample_colorpicker_1776114760775.png"
}

BRAIN_DIR = "/Users/davidmahler/.gemini/antigravity/brain/58f00244-3665-46fe-a8cf-782f3c9eb69a"
BASE_DIR = "/Users/davidmahler/Desktop/microAssets"

for ext_name, filename in BATCH.items():
    source_img = os.path.join(BRAIN_DIR, filename)
    target_icon_dir = os.path.join(BASE_DIR, ext_name, "icons")
    
    if not os.path.exists(target_icon_dir):
        print(f"Skipping {ext_name}, icon dir not found")
        continue

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

print("Batch 3 injection complete. Ready for screenshots.")
