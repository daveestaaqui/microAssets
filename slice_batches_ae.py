import process_grid_icons
import os

batches = {
    "a_1776014743963.png": ["css-gradient-generator", "font-identifier", "qr-code-generator", "wcag-auditor"],
    "b_1776014760468.png": ["tab-groups-saver", "page-ruler", "seo-content-pro", "sponsor-skipper"],
    "c_1776014776400.png": ["text-case-converter", "time-tracker", "url-shortener", "color-picker"],
    "d_1776014790451.png": ["image-resizer", "json-formatter", "markdown-editor", "lorem-ipsum-generator"],
    "e_1776014802474.png": ["base64-encoder", "password-generator", "uuid-generator", "cookie-manager"]
}

base_dir = "/Users/davidmahler/.gemini/antigravity/brain/6bdc5fa9-3872-4ab1-895b-625bd4f05588"
out_dir = "/Users/davidmahler/Desktop/microAssets"

for fname_suffix, ext_names in batches.items():
    # Find full match
    for f in os.listdir(base_dir):
        if f.startswith("icons_strict_batch_") and fname_suffix in f:
            full_path = os.path.join(base_dir, f)
            print(f"Slicing {f}...")
            process_grid_icons.slice_grid(full_path, out_dir, ext_names)

print("Done slicing!")
