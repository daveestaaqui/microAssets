import os
import json

base_dir = "/Users/davidmahler/Desktop/microAssets"

for d in os.listdir(base_dir):
    d_path = os.path.join(base_dir, d)
    if os.path.isdir(d_path):
        manifest_path = os.path.join(d_path, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                data = json.load(f)
            
            data["icons"] = {
                "16": "icon16.png",
                "48": "icon48.png",
                "128": "icon128.png"
            }
            if "action" in data:
                data["action"]["default_icon"] = {
                    "16": "icon16.png",
                    "48": "icon48.png",
                    "128": "icon128.png"
                }

            with open(manifest_path, 'w') as f:
                json.dump(data, f, indent=2)

print("Updated manifests.")
