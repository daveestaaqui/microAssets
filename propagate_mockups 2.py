import os
import shutil
from PIL import Image

brain_dir = '/Users/davidmahler/.gemini/antigravity/brain/58f00244-3665-46fe-a8cf-782f3c9eb69a/'
base_dir = '/Users/davidmahler/Desktop/microAssets'

mapping = {
    'sample_timestamp_1776112728263.png': 'timestamp-converter',
    'sample_link_1776112741529.png': 'link-checker',
    'sample_palette_1776112753862.png': 'color-palette-generator',
    'sample_privacy_1776112767920.png': 'privacy-scanner'
}

for img_file, ext_dir in mapping.items():
    src_path = os.path.join(brain_dir, img_file)
    icons_dir = os.path.join(base_dir, ext_dir, 'icons')
    
    if os.path.exists(src_path) and os.path.exists(icons_dir):
        # Master icon
        master_img = Image.open(src_path)
        
        # 128
        img_128 = master_img.resize((128, 128), Image.Resampling.LANCZOS)
        img_128.save(os.path.join(icons_dir, 'icon-128.png'))
        img_128.save(os.path.join(icons_dir, 'icon128.png'))
        img_128.save(os.path.join(icons_dir, 'icon.png'))
        
        # 48
        img_48 = master_img.resize((48, 48), Image.Resampling.LANCZOS)
        img_48.save(os.path.join(icons_dir, 'icon-48.png'))
        img_48.save(os.path.join(icons_dir, 'icon48.png'))
        
        # 16
        img_16 = master_img.resize((16, 16), Image.Resampling.LANCZOS)
        img_16.save(os.path.join(icons_dir, 'icon-16.png'))
        img_16.save(os.path.join(icons_dir, 'icon16.png'))
        
        print(f"Propagated assets for {ext_dir}")
    else:
        print(f"Missing paths for {ext_dir}")
