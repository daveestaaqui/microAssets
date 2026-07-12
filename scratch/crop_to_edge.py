from PIL import Image
import os

source_img_path = "/Users/davidmahler/.gemini/antigravity/brain/71a81ae7-6a4c-4701-bda1-718d846f136b/media__1783793454119.png"
out_avatar_path = "/Users/davidmahler/Desktop/microAssets/assets/instagram_avatar.png"
out_logo_path = "/Users/davidmahler/Desktop/microAssets/assets/logo-nav.png"

# Load image and convert to RGBA
img = Image.open(source_img_path).convert("RGBA")
width, height = img.size

# Process pixels to remove white background
data = img.getdata()
new_data = []

threshold = 240
for item in data:
    r, g, b, a = item
    if r > threshold and g > threshold and b > threshold:
        new_data.append((255, 255, 255, 0)) # Fully transparent
    else:
        new_data.append(item)

img.putdata(new_data)

# Find bounding box
bbox = img.getbbox()
if bbox:
    left, upper, right, lower = bbox
    print(f"Original Content bounding box: {bbox}")
    
    # Add a small buffer of 5 pixels
    buffer = 5
    b_left = max(0, left - buffer)
    b_upper = max(0, upper - buffer)
    b_right = min(width, right + buffer)
    b_lower = min(height, lower + buffer)
    
    buffered_bbox = (b_left, b_upper, b_right, b_lower)
    print(f"Buffered bounding box: {buffered_bbox}")
    
    # Crop to edge with small buffer
    cropped_img = img.crop(buffered_bbox)
    
    # Save as high-quality PNGs
    cropped_img.save(out_avatar_path, "PNG", compress_level=9, optimize=True)
    cropped_img.save(out_logo_path, "PNG", compress_level=9, optimize=True)
    
    print("Crop complete!")
    print(f"Saved: {out_avatar_path} ({cropped_img.size})")
    print(f"Saved: {out_logo_path} ({cropped_img.size})")
else:
    print("Error: Bounding box not found.")
