from PIL import Image

logo = Image.open('_landing_page/unified-logo.png').convert("RGBA")
w, h = logo.size
pixels = logo.load()

# Let's count non-empty pixels in each row
row_density = []
for y in range(h):
    count = 0
    for x in range(w):
        r, g, b, a = pixels[x, y]
        if a > 20 and not (r > 250 and g > 250 and b > 250):
            count += 1
    row_density.append(count)

# Find the lowest density row in the middle 30% of the image
mid_start = int(h * 0.35)
mid_end = int(h * 0.8)

min_count = w * w
best_y = mid_start

for y in range(mid_start, mid_end):
    if row_density[y] < min_count:
        min_count = row_density[y]
        best_y = y

print(f"Chosen split line at y={best_y} with {min_count} non-empty pixels")

gap_y = best_y

mushroom = logo.crop((0, 0, w, gap_y))
text = logo.crop((0, gap_y, w, h))

# Find bbox of mushroom to trim it perfectly
bg = Image.new(mushroom.mode, mushroom.size, mushroom.getpixel((0,0)))
diff = ImageChops.difference(mushroom, bg) if 'ImageChops' in globals() else mushroom
# simple bbox logic
def get_bbox(img):
    img_w, img_h = img.size
    px = img.load()
    min_x, max_x, min_y, max_y = img_w, 0, img_h, 0
    for iy in range(img_h):
        for ix in range(img_w):
            if px[ix, iy][3] > 10:
                if ix < min_x: min_x = ix
                if ix > max_x: max_x = ix
                if iy < min_y: min_y = iy
                if iy > max_y: max_y = iy
    if min_x > max_x: return (0,0,img_w,img_h)
    return (min_x, min_y, max_x+1, max_y+1)

mushroom = mushroom.crop(get_bbox(mushroom))
text = text.crop(get_bbox(text))

m_w, m_h = mushroom.size
t_w, t_h = text.size

target_text_h = int(m_h * 0.9) # Slogan slightly smaller than mushroom
if t_h > 0:
    scale = target_text_h / t_h
    new_t_w = int(t_w * scale)
    text_resized = text.resize((new_t_w, target_text_h), Image.Resampling.LANCZOS)
    
    spacing = 30
    out_w = m_w + spacing + new_t_w
    out_h = m_h
    
    out = Image.new("RGBA", (out_w, out_h), (255, 255, 255, 0))
    out.paste(mushroom, (0, 0))
    
    text_y = (out_h - target_text_h) // 2
    out.paste(text_resized, (m_w + spacing, text_y))
    
    out.save("_landing_page/unified-logo-nav.png")
    print("Successfully generated unified-logo-nav.png!")
else:
    print("Failed to crop text.")
