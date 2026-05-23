#!/usr/bin/env python3
"""
Process logo: 
1. True transparency (remove white bg)
2. Separate mushroom icon from "SPORLYWORKS" text
3. Generate all icon sizes
"""
import numpy as np
from PIL import Image

src = Image.open("/Users/davidmahler/Desktop/microAssets/assets/logo-full.png").convert("RGBA")
pixels = np.array(src, dtype=np.float64)
print(f"Source: {src.size[0]}x{src.size[1]}")

# ──── Remove white/light background ────
r, g, b, a = pixels[:,:,0], pixels[:,:,1], pixels[:,:,2], pixels[:,:,3]
brightness = (r + g + b) / 3.0
max_c = np.maximum(np.maximum(r, g), b)
min_c = np.minimum(np.minimum(r, g), b)
saturation = np.where(max_c > 0, (max_c - min_c) / max_c, 0)

# Background = bright + low saturation
is_bg = (brightness > 225) & (saturation < 0.10)

# Smooth edge transition
new_alpha = np.where(is_bg, 0.0, a)

# Edge feathering for anti-aliased edges
edge_zone = (brightness > 210) & (brightness <= 240) & (saturation < 0.18) & (~is_bg)
edge_alpha = np.clip(saturation / 0.18, 0, 1) * 255
new_alpha = np.where(edge_zone, np.minimum(new_alpha, edge_alpha), new_alpha)

pixels[:,:,3] = np.clip(new_alpha, 0, 255).astype(np.uint8)

# ──── Separate mushroom art from text ────
alpha_mask = pixels[:,:,3] > 10

# Find content bounds
rows_content = np.any(alpha_mask, axis=1)
cols_content = np.any(alpha_mask, axis=0)
rmin, rmax = np.where(rows_content)[0][[0, -1]]
cmin, cmax = np.where(cols_content)[0][[0, -1]]

# Analyze row density to find the gap between mushroom art and text
content_per_row = np.sum(alpha_mask[rmin:rmax+1, :], axis=1)
total_rows = rmax - rmin + 1

print(f"Content: rows {rmin}-{rmax}, cols {cmin}-{cmax}")
print(f"Total content height: {total_rows}px")

# Scan from bottom up. The text "SPORLYWORKS" is roughly the bottom 12% of the image.
# Find rows with very little content (gap between art and text)
gap_threshold = 5  # fewer than 5 pixels of content = gap row
gap_rows = []

# Start scanning from ~75% of the way down
scan_from = int(total_rows * 0.70)
for i in range(scan_from, total_rows):
    actual_row = rmin + i
    if content_per_row[i] < gap_threshold:
        gap_rows.append(actual_row)

if gap_rows:
    # The first gap row above the text is our cutoff
    art_bottom = gap_rows[0] - 1
    print(f"Found art/text gap at row {gap_rows[0]}. Art ends at row {art_bottom}")
else:
    # Fallback: just cut off the bottom ~13%
    art_bottom = rmin + int(total_rows * 0.87)
    print(f"No gap found. Using 87% cutoff at row {art_bottom}")

# ──── Crop the mushroom icon ────
art_top = rmin
art_left = cmin
art_right = cmax
art_w = art_right - art_left
art_h = art_bottom - art_top

# Make square with 6% padding
max_dim = max(art_w, art_h)
pad = int(max_dim * 0.06)
canvas = max_dim + pad * 2

# Center offsets
cx = (max_dim - art_w) // 2
cy = (max_dim - art_h) // 2

# Create the icon canvas
icon_img = Image.fromarray(pixels.astype(np.uint8))
icon_canvas = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))

# Paste the art centered
crop = icon_img.crop((art_left, art_top, art_right, art_bottom))
icon_canvas.paste(crop, (cx + pad, cy + pad))

print(f"Icon canvas: {canvas}x{canvas}")

out = "/Users/davidmahler/Desktop/microAssets/assets"

# Save master icon (mushroom only)
icon_canvas.save(f"{out}/icon-master.png", "PNG")
print(f"✓ icon-master.png")

# Generate all sizes
for sz in [512, 256, 128, 64, 48, 32, 16]:
    icon_canvas.resize((sz, sz), Image.LANCZOS).save(f"{out}/icon-{sz}.png", "PNG")
    print(f"✓ icon-{sz}.png")

# Favicon
fav = icon_canvas.resize((48, 48), Image.LANCZOS)
fav.save(f"{out}/favicon.ico", format="ICO", sizes=[(48, 48), (32, 32), (16, 16)])
print(f"✓ favicon.ico")

# Also save the full logo with text (transparent)
full_trans = Image.fromarray(pixels.astype(np.uint8))
full_crop = full_trans.crop((max(0, cmin-10), max(0, rmin-10), min(src.size[0], cmax+10), min(src.size[1], rmax+10)))
full_crop.save(f"{out}/logo-with-text.png", "PNG")
print(f"✓ logo-with-text.png ({full_crop.size[0]}x{full_crop.size[1]})")

print("\n✅ All done!")
