import os
import shutil
import subprocess

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
BRAIN_DIR = "/Users/davidmahler/.gemini/antigravity/brain/58f00244-3665-46fe-a8cf-782f3c9eb69a"

extensions = [
    ("color-picker-eyedropper", "sample_colorpicker_1776114760775.png"),
    ("qr-code-generator", "sample_qr_1776113696274.png"),
    ("page-ruler", "concept_pageruler_1776116354349.png"),
    ("url-encoder-decoder", "sample_url_1776113763859.png"),
    ("github-line-numbers", "concept_githublines_1776116364637.png"),
    ("wayback-machine-quick", "concept_wayback_1776116380999.png"),
    ("page-seo-analyzer", "sample_seo_1776114733937.png"),
    ("json-path-finder", "sample_json_1776113671527.png"),
    ("dark-mode-everywhere", "concept_darkmode_1776116395588.png"),
    ("sponsor-skipper", "concept_sponsor_1776116409653.png")
]

for ext_name, img_name in extensions:
    print(f"Processing {ext_name}...")
    source_img = os.path.join(BRAIN_DIR, img_name)
    target_img = os.path.join(BASE_DIR, ext_name, "icons", "icon.png")
    
    # 1. Copy icon
    shutil.copy(source_img, target_img)
    
    # 2. Crop icons to permutations
    subprocess.run(["python3", "crop_icons.py", ext_name], cwd=BASE_DIR, check=True)
    
    # 3. Inject boutique UI
    subprocess.run(["python3", "inject_boutique_ui.py", ext_name], cwd=BASE_DIR, check=True)

print("Batch 8 absolute success.")
