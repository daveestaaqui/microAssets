from PIL import Image
import os

img_path = "/Users/davidmahler/.gemini/antigravity/brain/0bba0b7e-2d9c-4a20-bbeb-cc0a9b251610/media__1779238897541.jpg"
im = Image.open(img_path)
print(f"Dimensions: {im.size}")
print(f"Format: {im.format}")
print(f"Mode: {im.mode}")
