from PIL import Image
import os

source_path = "/Users/davidmahler/Desktop/microAssets/assets/icon-512.png"
target_path = "/Users/davidmahler/Desktop/microAssets/assets/logo-nav.png"

# Load image
img = Image.open(source_path)

# Resize to 400x400 (optimal for 200px display at 2x density)
img_resized = img.resize((400, 400), Image.Resampling.LANCZOS)

# Save with maximum PNG compression
img_resized.save(target_path, "PNG", compress_level=9, optimize=True)

size_orig = os.path.getsize(source_path)
size_new = os.path.getsize(target_path)

print(f"Original size (512x512): {size_orig} bytes ({size_orig/1024:.1f} KB)")
print(f"Optimized size (400x400): {size_new} bytes ({size_new/1024:.1f} KB)")
