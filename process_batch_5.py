import os
import shutil
import subprocess

BATCH = {
    "carbon-footprint-checker": "concept_carbonfootprint_1776115200009_1776115329402.png",
    "calculator-pro": "concept_calculator_1776115200008_1776115317704.png",
    "cache-clearer": "concept_cacheclear_1776115200007_1776115304149.png",
    "b64-image-encoder": "concept_b64image_1776115200006_1776115290463.png",
    "auto-refresh": "concept_autorefresh_1776115200005_1776115276436.png",
    "api-tester-pro": "concept_apitester_1776115200004_1776115263107.png",
    "amazon-wide-mode": "concept_amazonwide_1776115200003_1776115247851.png",
    "amazon-fake-review-skimmer": "concept_amazonreview_1776115200002_1776115233408.png",
    "ai-content-bouncer": "concept_bouncer_1776115200001_1776115219272.png",
    "ad-blocker-pro": "concept_adblock_1776115200000_1776115202942.png"
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

print("Batch 5 injection complete. Ready for screenshots.")
