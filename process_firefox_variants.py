import os
import shutil
import subprocess

BASE_DIR = "/Users/davidmahler/Desktop/microAssets"
pending_file = "/Users/davidmahler/.gemini/antigravity/brain/58f00244-3665-46fe-a8cf-782f3c9eb69a/pending_extensions.txt"

with open(pending_file) as f:
    pending = [l.strip() for l in f if l.strip()]

processed_firefox = []

for ext_name in pending:
    if ext_name.endswith("-firefox"):
        base_ext = ext_name.removesuffix("-firefox")
        base_promo = os.path.join(BASE_DIR, "promo", f"{base_ext}_macbook.png")
        
        # We also check if the base extension icons were updated by looking for inject_boutique_ui effects.
        # Actually, let's just check if base_ext/icons/icon.png is > 200KB (meaning it's our new huge concept image)
        # Or let's just do: if the base_ext/icons/icon.png is larger than the target.
        base_icon = os.path.join(BASE_DIR, base_ext, "icons", "icon.png")
        target_icon = os.path.join(BASE_DIR, ext_name, "icons", "icon.png")
        
        if os.path.exists(base_icon) and os.path.exists(target_icon):
            if os.stat(base_icon).st_size > os.stat(target_icon).st_size * 2: # heuristic: our new images are much larger
                print(f"Applying updated brand to {ext_name} based on {base_ext}")
                target_icon_dir = os.path.join(BASE_DIR, ext_name, "icons")
                
                for f in os.listdir(os.path.join(BASE_DIR, base_ext, "icons")):
                    if f.endswith(".png"):
                        src = os.path.join(BASE_DIR, base_ext, "icons", f)
                        dst = os.path.join(target_icon_dir, f)
                        shutil.copy(src, dst)
                
                # Inject Boutique UI
                subprocess.run(["python3", "inject_boutique_ui.py", ext_name], cwd=BASE_DIR, check=True)
                processed_firefox.append(ext_name)

print(f"Processed {len(processed_firefox)} -firefox extensions.")
