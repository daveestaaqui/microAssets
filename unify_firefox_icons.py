import os
import shutil

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"

# Get all Firefox extensions
firefox_dirs = [d for d in os.listdir(BASE_DIR) if d.endswith('-firefox') and os.path.isdir(os.path.join(BASE_DIR, d))]

synced = 0
for f_ext in firefox_dirs:
    base_ext = f_ext.removesuffix('-firefox')
    base_icon_dir = os.path.join(BASE_DIR, base_ext, 'icons')
    firefox_icon_dir = os.path.join(BASE_DIR, f_ext, 'icons')
    
    # Optional: ensure manifest icons dict is also correct in manifest.json
    import json
    mani_path = os.path.join(BASE_DIR, f_ext, 'manifest.json')
    if os.path.exists(base_icon_dir) and os.path.exists(mani_path):
        import shutil
        if os.path.exists(firefox_icon_dir):
            shutil.rmtree(firefox_icon_dir) # clear generic
        shutil.copytree(base_icon_dir, firefox_icon_dir)
        
        # update the root level icons too (some extensions place 16/48/128 in root)
        for size in [16, 48, 128]:
            base_png = os.path.join(BASE_DIR, base_ext, f'icon{size}.png')
            if os.path.exists(base_png):
                shutil.copy(base_png, os.path.join(BASE_DIR, f_ext, f'icon{size}.png'))
                
        # update manifest.json to point to the icons dir exactly like base
        with open(mani_path, 'r') as f:
            mani_data = json.load(f)
            
        mani_data["icons"] = {
            "16": "icons/icon16.png",
            "48": "icons/icon48.png",
            "128": "icons/icon128.png"
        }
        if "browser_action" in mani_data:
            mani_data["browser_action"]["default_icon"] = {
                "16": "icons/icon16.png",
                "48": "icons/icon48.png",
                "128": "icons/icon128.png"
            }
        
        with open(mani_path, 'w') as f:
            json.dump(mani_data, f, indent=2)
            
        synced += 1

print(f"Synced {synced} Firefox extensions with perfect base logos.")
