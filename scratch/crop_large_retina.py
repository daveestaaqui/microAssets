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
    # Manually target the actual mushroom cluster coordinates (X: 180-350, Y: 178-362)
    # This discards the left-side stray watermark/noise which shifted the logo off-center.
    b_left = 180
    b_upper = 178
    b_right = 350
    b_lower = 362
    
    buffered_bbox = (b_left, b_upper, b_right, b_lower)
    print(f"Targeted mushroom cluster bounding box: {buffered_bbox}")
    
    # Crop to edge of the actual mushrooms
    cropped_img = img.crop(buffered_bbox)
    c_w, c_h = cropped_img.size
    
    # Scale up proportionally (target 400px height for perfect 2x Retina resolution!)
    target_height = 400
    target_width = int(c_w * (target_height / c_h))
    
    # Resize using high-quality Lanzcos interpolation
    highres_img = cropped_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Save as high-quality PNGs
    highres_img.save(out_avatar_path, "PNG", compress_level=9, optimize=True)
    highres_img.save(out_logo_path, "PNG", compress_level=9, optimize=True)
    
    print("Crop and resize complete!")
    print(f"Original cropped size: {cropped_img.size}")
    print(f"New 30% enlarged Retina size: {highres_img.size} ({os.path.getsize(out_logo_path)/1024:.1f} KB)")
else:
    print("Error: Bounding box not found.")
