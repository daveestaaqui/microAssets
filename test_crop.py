from PIL import Image, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

logo = Image.open('_landing_page/unified-logo.png')
# Assuming mushroom is at the top and text is at the bottom.
# Let's see the bounding box of the whole thing.
logo = trim(logo)
print("Trimmed overall size:", logo.size)

# Scan horizontal lines to find the gap between the mushroom and the text.
w, h = logo.size
pixels = logo.load()
bg_color = pixels[0, 0]

gap_start = -1
gap_end = -1
in_gap = False

for y in range(h):
    row_is_empty = True
    for x in range(w):
        if pixels[x, y][:3] != (255, 255, 255): # Assuming white or transparent background
            if len(pixels[x,y]) == 4 and pixels[x,y][3] > 10:
                row_is_empty = False
                break
            elif len(pixels[x,y]) == 3:
                row_is_empty = False
                break
    
    if row_is_empty and not in_gap and y > h * 0.2:
        in_gap = True
        gap_start = y
    elif not row_is_empty and in_gap:
        in_gap = False
        gap_end = y
        break # First gap separates mushroom and text

print("Gap between mushroom and text:", gap_start, "to", gap_end)
