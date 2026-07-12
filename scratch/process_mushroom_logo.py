from PIL import Image, ImageChops
import os

source_img_path = "/Users/davidmahler/.gemini/antigravity/brain/71a81ae7-6a4c-4701-bda1-718d846f136b/media__1783793024628.png"
out_avatar_path = "/Users/davidmahler/Desktop/microAssets/assets/instagram_avatar.png"
out_logo_path = "/Users/davidmahler/Desktop/microAssets/assets/logo-nav.png"

# Load image and convert to RGBA
img = Image.open(source_img_path).convert("RGBA")
width, height = img.size

# Process pixels to remove white background
data = img.getdata()
new_data = []

# Detect near-white background (RGB values close to 255)
threshold = 240
for item in data:
    r, g, b, a = item
    if r > threshold and g > threshold and b > threshold:
        new_data.append((255, 255, 255, 0)) # Make pixel fully transparent
    else:
        new_data.append(item)

img.putdata(new_data)

# Find bounding box of non-transparent content
# Image.getbbox() returns (left, upper, right, lower)
bbox = img.getbbox()
if bbox:
    left, upper, right, lower = bbox
    print(f"Content bounding box: {bbox}")
    
    # Crop content
    cropped_img = img.crop(bbox)
    c_w, c_h = cropped_img.size
    
    # Determine square canvas size (add 10% padding)
    max_dim = max(c_w, c_h)
    pad = int(max_dim * 0.05)
    canvas_size = max_dim + (pad * 2)
    
    # Create new square canvas with transparent background
    square_canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    
    # Paste cropped content centered
    offset_x = (canvas_size - c_w) // 2
    offset_y = (canvas_size - c_h) // 2
    square_canvas.paste(cropped_img, (offset_x, offset_y), cropped_img)
    
    # Resize to targets
    avatar_resized = square_canvas.resize((500, 500), Image.Resampling.LANCZOS)
    logo_resized = square_canvas.resize((400, 400), Image.Resampling.LANCZOS)
    
    # Save
    avatar_resized.save(out_avatar_path, "PNG", compress_level=9, optimize=True)
    logo_resized.save(out_logo_path, "PNG", compress_level=9, optimize=True)
    
    print(f"Successfully processed logo!")
    print(f"Saved Instagram Avatar (500x500 transparent PNG): {out_avatar_path} ({os.path.getsize(out_avatar_path)/1024:.1f} KB)")
    print(f"Saved Optimized Website Logo (400x400 transparent PNG): {out_logo_path} ({os.path.getsize(out_logo_path)/1024:.1f} KB)")
else:
    print("Error: Bounding box not found, image might be blank.")
