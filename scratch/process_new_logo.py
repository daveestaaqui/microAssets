#!/usr/bin/env python3
import numpy as np
from PIL import Image
import os

# Paths
brain_img = "/Users/davidmahler/.gemini/antigravity/brain/0bba0b7e-2d9c-4a20-bbeb-cc0a9b251610/media__1779238897541.jpg"
out_dir = "/Users/davidmahler/Desktop/microAssets/assets"

# 1. Overwrite logo-full.png with the new source image (converting to PNG)
src = Image.open(brain_img).convert("RGBA")
src.save(f"{out_dir}/logo-full.png", "PNG")
print("✓ Overwrote assets/logo-full.png")

# 2. Crop top-left region for parchment background tile (x=20..276, y=20..276)
# This avoids any corner vignettes while taking a clean 256x256 patch
parchment_tile = src.crop((20, 20, 276, 276)).convert("RGB")
parchment_tile.save(f"{out_dir}/parchment-tile.jpg", "JPEG", quality=95)
print("✓ Created assets/parchment-tile.jpg from logo background")

# 3. Process transparency and generate icons
pixels = np.array(src, dtype=np.float64)
r, g, b, a = pixels[:,:,0], pixels[:,:,1], pixels[:,:,2], pixels[:,:,3]
brightness = (r + g + b) / 3.0
max_c = np.maximum(np.maximum(r, g), b)
min_c = np.minimum(np.minimum(r, g), b)
saturation = np.where(max_c > 0, (max_c - min_c) / max_c, 0)

# Optimized thresholds for this specific image's cream background
is_bg = (brightness > 220) & (saturation < 0.12)
new_alpha = np.where(is_bg, 0.0, a)

# Feathering for soft anti-aliased borders
edge_zone = (brightness > 200) & (brightness <= 235) & (saturation < 0.18) & (~is_bg)
edge_alpha = np.clip(saturation / 0.18, 0, 1) * 255
new_alpha = np.where(edge_zone, np.minimum(new_alpha, edge_alpha), new_alpha)

pixels[:,:,3] = np.clip(new_alpha, 0, 255).astype(np.uint8)

# Find content bounds
alpha_mask = pixels[:,:,3] > 10
rows_content = np.any(alpha_mask, axis=1)
cols_content = np.any(alpha_mask, axis=0)
rmin, rmax = np.where(rows_content)[0][[0, -1]]
cmin, cmax = np.where(cols_content)[0][[0, -1]]

content_per_row = np.sum(alpha_mask[rmin:rmax+1, :], axis=1)
total_rows = rmax - rmin + 1

print(f"Content bounds: rows {rmin}-{rmax}, cols {cmin}-{cmax}")
print(f"Content height: {total_rows}px")

# Find the gap between the mushroom art and "SPORLYWORKS" text
gap_threshold = 4
gap_rows = []
scan_from = int(total_rows * 0.65)
for i in range(scan_from, total_rows):
    actual_row = rmin + i
    if content_per_row[i] < gap_threshold:
        gap_rows.append(actual_row)

if gap_rows:
    art_bottom = gap_rows[0] - 1
    print(f"Found art/text gap at row {gap_rows[0]}. Mushroom art ends at row {art_bottom}")
else:
    art_bottom = rmin + int(total_rows * 0.85)
    print(f"No gap found. Using 85% fallback cutoff at row {art_bottom}")

# Crop the mushroom icon
art_top = rmin
art_left = cmin
art_right = cmax
art_w = art_right - art_left
art_h = art_bottom - art_top

# Center the mushroom on a square canvas with padding
max_dim = max(art_w, art_h)
pad = int(max_dim * 0.06)
canvas_size = max_dim + pad * 2
cx = (max_dim - art_w) // 2
cy = (max_dim - art_h) // 2

icon_img = Image.fromarray(pixels.astype(np.uint8))
icon_canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

# Crop and paste centered
crop = icon_img.crop((art_left, art_top, art_right, art_bottom))
icon_canvas.paste(crop, (cx + pad, cy + pad))
print(f"Generated square icon master of size {canvas_size}x{canvas_size}")

# Save master icon (mushroom art only)
icon_canvas.save(f"{out_dir}/icon-master.png", "PNG")
print("✓ Saved assets/icon-master.png")

# Generate all required icon sizes
for sz in [512, 256, 128, 64, 48, 32, 16]:
    icon_canvas.resize((sz, sz), Image.LANCZOS).save(f"{out_dir}/icon-{sz}.png", "PNG")
    print(f"✓ Generated assets/icon-{sz}.png")

# Generate Favicon
fav = icon_canvas.resize((48, 48), Image.LANCZOS)
fav.save(f"{out_dir}/favicon.ico", format="ICO", sizes=[(48, 48), (32, 32), (16, 16)])
print("✓ Generated assets/favicon.ico")

# Save full transparent logo (mushrooms + text)
full_trans = Image.fromarray(pixels.astype(np.uint8))
full_crop = full_trans.crop((max(0, cmin-10), max(0, rmin-10), min(src.size[0], cmax+10), min(src.size[1], rmax+10)))
full_crop.save(f"{out_dir}/logo-with-text.png", "PNG")
print(f"✓ Generated assets/logo-with-text.png ({full_crop.size[0]}x{full_crop.size[1]})")

print("\n🎉 Logo processing successfully completed!")
