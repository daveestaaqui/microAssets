from PIL import Image
import numpy as np

img_path = "/Users/davidmahler/.gemini/antigravity/brain/0bba0b7e-2d9c-4a20-bbeb-cc0a9b251610/media__1779238897541.jpg"
im = Image.open(img_path).convert("RGBA")
pixels = np.array(im, dtype=np.float64)
# Take top-left 50x50 region
tl = pixels[0:50, 0:50]
r, g, b = tl[:,:,0], tl[:,:,1], tl[:,:,2]
brightness = (r + g + b) / 3.0
max_c = np.maximum(np.maximum(r, g), b)
min_c = np.minimum(np.minimum(r, g), b)
saturation = np.where(max_c > 0, (max_c - min_c) / max_c, 0)

print("Brightness range:", brightness.min(), "to", brightness.max())
print("Average brightness:", brightness.mean())
print("Saturation range:", saturation.min(), "to", saturation.max())
print("Average saturation:", saturation.mean())
