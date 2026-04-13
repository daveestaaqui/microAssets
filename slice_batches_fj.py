import process_grid_icons
import os

batches = {
    "f_1776014846423.png": ["html-formatter", "random-string-generator", "timestamp-converter", "url-encoder-decoder"],
    "g_1776014859572.png": ["b64-image-encoder", "character-counter", "word-counter", "case-converter"],
    "h_1776014872556.png": ["regex-tester", "cron-parser", "jwt-decoder", "xml-formatter"],
    "i_1776014888779.png": ["yaml-to-json", "json-to-yaml", "hash-generator", "mac-address-generator"],
    "j_1776014900823.png": ["user-agent-switcher", "cache-clearer", "cookie-editor", "local-storage-manager"]
}

base_dir = "/Users/davidmahler/.gemini/antigravity/brain/6bdc5fa9-3872-4ab1-895b-625bd4f05588"
out_dir = "/Users/davidmahler/Desktop/microAssets"

for fname_suffix, ext_names in batches.items():
    for f in os.listdir(base_dir):
        if f.startswith("icons_strict_batch_") and fname_suffix in f:
            full_path = os.path.join(base_dir, f)
            print(f"Slicing {f}...")
            process_grid_icons.slice_grid(full_path, out_dir, ext_names)

print("Batch F-J sliced successfully!")
