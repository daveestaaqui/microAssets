import os
import shutil

def deploy():
    src_dir = "_landing_page"
    dest_dir = "." # The root directory
    
    files_to_copy = ["index.html", "style.css", "unified-logo.png", "logo-nav.png", "omnisuite-logo.png", "parchment-bg-opt.jpg"]
    
    for f in files_to_copy:
        src = os.path.join(src_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, f)
            print(f"Copied {f} to root.")
        else:
            print(f"Warning: {src} not found.")

if __name__ == "__main__":
    deploy()
