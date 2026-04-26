import os, shutil, subprocess
BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
BRAIN_DIR = "/Users/davidmahler/.gemini/antigravity/brain/58f00244-3665-46fe-a8cf-782f3c9eb69a"
extensions = [
    ("llm-privacy-scrub", "sample_privacy_1776112767920.png"),
    ("gdocs-focus-mode", "concept_darkmode_1776116395588.png"),
    ("regex-tester", "concept_apitester_1776115200004_1776115263107.png"),
    ("network-monitor-pro", "concept_networkspeed_1776115913730.png"),
    ("tab-suspender", "concept_diffchecker_1776115811488.png"),
    ("time-tracker", "concept_readingtime_1776115824702.png"),
    ("cookie-manager", "sample_cookie_1776113644210.png"),
    ("google-dark-search", "concept_darkmode_1776116395588.png"),
    ("json-csv-converter", "sample_json_1776113671527.png"),
    ("screenshot-capture", "sample_screenshot_1776113683336.png"),
    ("diff-viewer", "concept_diffchecker2_1776115962601.png"),
    ("css-inspector-pro", "concept_cssgrad_1776115400009_1776115666702.png"),
    ("http-status-checker", "concept_diffchecker2_1776115962601.png"),
    ("markdown-preview", "sample_markdown_1776113722362.png"),
    ("json-formatter", "sample_json_1776113671527.png"),
    ("github-quick-stats", "concept_githublines_1776116364637.png"),
    ("word-counter", "sample_word_1776113736083.png"),
    ("url-shortener", "sample_url_1776113763859.png"),
    ("reading-mode", "concept_readingtime_1776115824702.png"),
]

for ext_name, img_name in extensions:
    print(f"Processing {ext_name}...")
    source_img = os.path.join(BRAIN_DIR, img_name)
    target_img = os.path.join(BASE_DIR, ext_name, "icons", "icon.png")
    shutil.copy(source_img, target_img)
    subprocess.run(["python3", "crop_icons.py", ext_name], cwd=BASE_DIR, check=True)
    subprocess.run(["python3", "inject_boutique_ui.py", ext_name], cwd=BASE_DIR, check=True)
print("Batch 9 absolute success.")
