import os, shutil, subprocess

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
BRAIN_DIR = "/Users/davidmahler/.gemini/antigravity/brain/58f00244-3665-46fe-a8cf-782f3c9eb69a"

extensions = [
    ("jira-declutter", "sample_cookie_1776113644210.png"),
    ("reddit-redirect", "concept_wayback_1776116380999.png"),
    ("lorem-ipsum-generator", "sample_word_1776113736083.png"),
    ("text-case-converter", "sample_font_1776114722254.png"),
    ("instagram-clean-feed", "concept_bouncer_1776115200001_1776115219272.png"),
    ("http-headers", "concept_apitester_1776115200004_1776115263107.png"),
    ("wcag-auditor", "sample_seo_1776114733937.png"),
    ("invoice-extractor", "concept_contract_1776115400003_1776115591233.png"),
    ("responsive-viewer", "concept_cssbox_1776115400007_1776115640958.png"),
    ("og-previewer", "sample_screenshot_1776113683336.png"),
    ("meet-zoom-automute", "concept_darkmode_1776116395588.png"),
    ("hash-generator", "sample_password_1776114644431.png"),
    ("website-monitor-pro", "concept_networkspeed_1776115913730.png"),
    ("jwt-decoder", "sample_base64_1776115100843.png"),
    ("linkedin-hide-feed", "concept_bouncer_1776115200001_1776115219272.png"),
    ("user-agent-switcher", "concept_robots_1776115889208.png"),
    ("form-filler-pro", "concept_contract_1776115400003_1776115591233.png"),
    ("meta-tag-editor", "sample_seo_1776114733937.png"),
    ("quick-notepad", "sample_markdown_1776113722362.png")
]

for ext_name, img_name in extensions:
    print(f"Processing {ext_name}...")
    source_img = os.path.join(BRAIN_DIR, img_name)
    target_img = os.path.join(BASE_DIR, ext_name, "icons", "icon.png")
    shutil.copy(source_img, target_img)
    subprocess.run(["python3", "crop_icons.py", ext_name], cwd=BASE_DIR, check=True)
    subprocess.run(["python3", "inject_boutique_ui.py", ext_name], cwd=BASE_DIR, check=True)

print("Batch 10 absolute success.")
